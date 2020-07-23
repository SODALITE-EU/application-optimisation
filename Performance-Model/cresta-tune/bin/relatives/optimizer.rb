#!/usr/bin/ruby
#
# Autotuner Mockup Driver
#
# Harvey Richardson Cray UK 2013-2014, 2016, 2017
#
# Copyright (C) 2013-2016 Cray UK Ltd
# License: Not licensed, CRESTA partner internal use only
#
#

require_relative "worklist"

# The Optimizer finds the best set of parameters
class Optimizer
 
 def initialize(control,config)
  # get references 
  @control = control
  @config = config
  @work = Worklist.new(@control,@config)
  # Store some history when we execute
  @seq=0
  @firstrun_seq=Array.new
  @lastrun_seq=Array.new
  @optimized_run_id=Array.new
  @optimized_params=Array.new
  @default_params_run_id=Array.new
 end

 def firstrun_seq
  @firstrun_seq
 end
 def lastrun_seq
  @lastrun_seq
 end
 def optimized_run_id
  @optimized_run_id
 end
 def optimized_params
  @optimized_params
 end
 def default_params_run_id
  @default_params_run_id
 end
 def num_calls
  @seq
 end
 def work
  @work
 end
 
 
 def run(overload_params)

 bestrun=-1 # so we can tell if we set it
 @firstrun_seq[@seq] = @work.seq
 @optimized_run_id[@seq] = @work.seq
 @default_params_run_id[@seq] = -1

 # Start by finding independent parameters
 # For each of these find best using default parameters for all others
 # Then work on sets of dependent parameters 

 # Have rolling param=value hash that is passed to Worklist
 # Work through independnet parameters and either fix immediately (one value)
 # or tune for best 
 # Then having fixed those work through sets of dependent parameters
 # choosing best set of parameters

 param_value=Hash.new # current parameter value, filled in as we progress

 # Start with default values

 @config.params.each { |name,param| param_value[name]=param.default }

 if $debug
   pretty=""
   PP.singleline_pp(param_value,pretty)
   puts "Optimizer: param_value from defaults #{pretty}" 
  end

 # Take into account any overriding of these defaults if we were
 # called from a configuration run
 
 overload_params.each { |name,v| param_value[name]=v }

 if $debug
   pretty=""
   PP.singleline_pp(overload_params,pretty)
   puts "Optimizer: overload_params #{pretty}" 
   pretty=""
   PP.singleline_pp(param_value,pretty)
   puts "Optimizer: param_value with overloads #{pretty}" 
  end

 default_run_params = Hash[param_value] # used to find run that matches
 # remove generated params from this list
 @config.gparams.merge(@config.cparams).each { |pname,v|
   default_run_params.delete(pname)
  }

 if $debug
   pretty=""
   PP.singleline_pp(default_run_params,pretty)
   puts "Optimizer: Default run_params is #{pretty}" 
  end

 current_param_value=Hash[param_value]
 
 if $debug
   pretty=""
   PP.singleline_pp(current_param_value,pretty)
   puts "Optimizer: Starting with params #{pretty}" 
  end

 # First check if any collections/parameters are fixed

 $log.message(MyLogger::STDOUT|MyLogger::FILE,"Starting Optimizer\n\n")

 # Need one here so we can get it out of the block below 
 constraints_ok = true
 
 @config.ipool.each { |p|

  if (p.class==String) 
    if (@config.params[p].nvalues == 1) then
      str = "parameter #{p} "
      if (!@config.params[p].inscope)
       str << "is not in scope and "
      end
      str << "has a single value of #{@config.params[p].default}"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
     elsif (!@config.params[p].inscope)
      str = "parameter #{p} is not in scope and has default value of #{@config.params[p].default}"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
     else

     starting_param_value=Hash[current_param_value] # we compare changes to this
     # remove generated params from this list
     @config.gparams.merge(@config.cparams).each { |pname,v|
       starting_param_value.delete(pname)
      }

      if $debug
        pretty=""
        PP.singleline_pp(starting_param_value,pretty)
        puts "Optimizer: (ind.) starting_param_value = #{pretty}" 
       end

     # Single parameter set of values
     str = "parameter #{p} can be independently tuned:"
     $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
     @work.new_sequence
      # Track if we rejected runs due to constraints
      seq_nruns = 0;
      seq_nrejects = 0;
      @config.params[p].value.each { |v|
        current_param_value[p]=v
#       At this point need to update any generated parameters
        @config.gparams.each { |gpname,gp|
          current_param_value[gpname] = ""
          gp.factors.each { |f|
            if (current_param_value[f] != "unset")
            if (current_param_value[gpname] == "")
               current_param_value[gpname] << "#{current_param_value[f]}"
            else 
              current_param_value[gpname] << " #{current_param_value[f]}"
             end
            end
           }
         }
#       Now for constraint expression generated parameters
         @config.cparams.each { |cpname,cp|
#           puts "Scanning cparam #{cpname}"
           cexpr = Param.evalParamExpression(cp.expression,current_param_value,@config.params)
           cexpr = cexpr.to_i if cp.type == "int"
#           puts "Expression is #{cexpr}"
           current_param_value[cpname] = cexpr    
         }        
#         Check that constraints don't stop us doing this run
         constraints_ok = true
         @config.constraints.each{ |expr|
           constraints_ok = constraints_ok && 
              Param.evalParamExpression(expr,current_param_value,@config.params)
          }
        if constraints_ok
          seq_nruns += 1
          @work.pushrun(current_param_value)
          if current_param_value.contains?(default_run_params)
            @default_params_run_id[@seq] = @work.seq-1
           end
         else 
          seq_nrejects += 1
         end
       }

      nruns = @work.seq_nruns;
      if seq_nrejects > 0   
        string=" Constraints allowed #{seq_nruns} and prevented #{seq_nrejects} runs"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,string)
        $log.message(MyLogger::STDOUT|MyLogger::FILE,"\n")
       end
      if nruns == 0
        abort("There are no valid runs to execute, cannot continue!")
       end
      str = " Choose best from the following #{nruns} runs\n"
      str << "#{@work.to_s}"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
      $log.message(MyLogger::STDOUT|MyLogger::FILE,"\n")

      @work.execute
      # Get best parameter set
      $log.message(MyLogger::STDOUT|MyLogger::FILE,"")
      bestrun=@work.bestrun
      bestmetric=@work.metric[bestrun]
      str = "Best run was run #{bestrun} with metric #{bestmetric}"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)

      if @work.run_params[bestrun].contains?(starting_param_value)
        str =  "... no change in parameters"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
       else 
        string="... new values chosen:"
        starting_param_value.each { |p,v|
          if (@work.run_params[bestrun][p] != v)
            string << " #{p}=#{@work.run_params[bestrun][p]}"
            current_param_value[p]=@work.run_params[bestrun][p]
           end
         }
         string << "\n\n"
         $log.message(MyLogger::STDOUT|MyLogger::FILE,string)
         @optimized_run_id[@seq] = bestrun
       end

       # We need to cater for the situation that a run not acceptred
       # due to constraints has set current_param_value to something invalid
        starting_param_value.each { |p,v|
          if (@work.run_params[bestrun][p] != current_param_value[p])
            puts " resetting current_param_value[#{p}] to #{@work.run_params[bestrun][p]} for next set" if $debug
            current_param_value[p]=@work.run_params[bestrun][p]
           end
         }

     end
    next
    #  
   end

   # We have a dependent set

   # BUG There was a bug here because we did not check if any of the
   # dependent parameters was in scope

   dparams=p.dup
   string="parameters"
   dparams.each {|dp| string << " #{dp}" }
   string << " are dependent\n"
   # string << " Choose best values from following runs"
   $log.message(MyLogger::STDOUT|MyLogger::FILE,string)

   # Now do checking for parameters not in scope
   # If they are remove them

   dparams.delete_if do |dp|
     if (!@config.params[dp].inscope)
      str = "parameter #{dp} is not in scope and has default value of #{@config.params[dp].default}"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
      true
     end
    end

   if (dparams.size < 1) 
     next
    end

   @work.new_sequence
      # Track if we rejected runs due to constraints
      seq_nruns = 0;
      seq_nrejects = 0;
   starting_param_value=Hash[current_param_value]
   # remove generated params from this list
   @config.gparams.merge(@config.cparams).each { |pname,v|
     starting_param_value.delete(pname)
    }

   puts "Optimizer: B starting_param_value = #{starting_param_value}" if $debug

   # Calculate left counts of parameter values as we scan parameters
   dp_sizes=Array.new
   dp_products=Array.new
   for i in 0..dparams.size-1
     dp_sizes[i]=@config.params[dparams[i]].nvalues
     if (i==0)
       dp_products[i]=dp_sizes[i]
      else
       dp_products[i]=dp_sizes[i]*dp_products[i-1]
      end
    end
    # Now work across each combination choosing from values
    for k in 0..dp_products[dparams.size-1]-1
    # string="  Combination #{k}: "
     for i in 0..dparams.size-1
       if (i==0)
         ipos = k % dp_sizes[i]
        else
         ipos=( k / dp_products[i-1] )% dp_sizes[i]
        end
     #  puts " #{dparams[i]}= #{@config.params[dparams[i]].value[ipos]}"
        current_param_value[dparams[i]]=@config.params[dparams[i]].value[ipos]
       end
#       At this point need to update any generated parameters
        @config.gparams.each { |gpname,gp|
          current_param_value[gpname] = ""
          gp.factors.each { |f|
           if (current_param_value[f] != "unset")
            if (current_param_value[gpname] == "")
               current_param_value[gpname] << "#{current_param_value[f]}"
            else 
              current_param_value[gpname] << " #{current_param_value[f]}"
             end
            end
           }
         }
#       Now for constraint expression generated parameters
         @config.cparams.each { |cpname,cp|
           cexpr = Param.evalParamExpression(cp.expression,current_param_value,@config.params)
           cexpr = cexpr.to_i if cp.type == "int"
           current_param_value[cpname] = cexpr    
         }        

#       Check that constraints don't stop us doing this run
        constraints_ok = true
        @config.constraints.each{ |expr|
          constraints_ok = constraints_ok && 
             Param.evalParamExpression(expr,current_param_value,@config.params)
         }

        if constraints_ok
          seq_nruns += 1
          @work.pushrun(current_param_value)
          if current_param_value.contains?(default_run_params)
            @default_params_run_id[@seq] = @work.seq-1
           end
         else 
          seq_nrejects += 1
         end

    end
    nruns = @work.seq_nruns;
    if seq_nrejects > 0   
      string=" Constraints allowed #{seq_nruns} and prevented #{seq_nrejects} runs"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,string)
      $log.message(MyLogger::STDOUT|MyLogger::FILE,"\n")
     end
     
    if nruns == 0
      abort("There are no valid runs to execute, cannot continue!")
     end
    string = " Choose best from the following #{nruns} runs\n"
    string << "#{@work.to_s}"
    $log.message(MyLogger::STDOUT|MyLogger::FILE,string)
    $log.message(MyLogger::STDOUT|MyLogger::FILE,"\n")

    @work.execute
    $log.message(MyLogger::STDOUT|MyLogger::FILE,"")

    bestrun=@work.bestrun
    bestmetric=@work.metric[bestrun]
    str = "Best run was #{bestrun} with metric #{bestmetric}"
    $log.message(MyLogger::STDOUT|MyLogger::FILE,str)

    if @work.run_params[bestrun].contains?(starting_param_value)
      str = "... no change in parameters"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
     else 
      string="... new values chosen:"
      starting_param_value.each { |p,v|
        if (@work.run_params[bestrun][p] != v)
          string << " #{p}=#{@work.run_params[bestrun][p]}"
          current_param_value[p]=@work.run_params[bestrun][p]
         end
       }
      string << "\n\n"
      $log.message(MyLogger::STDOUT|MyLogger::FILE,string)
      @optimized_run_id[@seq] = bestrun
     end

    # We need to cater for the situation that a run not acceptred
    # due to constraints has set current_param_value to something invalid
    starting_param_value.each { |p,v|
      if (@work.run_params[bestrun][p] != current_param_value[p])
         puts " resetting current_param_value[#{p}] to #{@work.run_params[bestrun][p]} for next set" if $debug
         current_param_value[p]=@work.run_params[bestrun][p]
        end
     }
  
   }

  if bestrun < 0
    @optimized_params[@seq] = param_value
   else
    @optimized_params[@seq] = @work.run_params[bestrun]
   end

  string = "\nFinal Optimized Parameters are:\n\n"

  @optimized_params[@seq].each { |p,v|
    string << " #{p}=#{v}\n"
   }
  if bestrun < 1 
   string << "\n (this was the default set of values)\n"
   end
  $log.message(MyLogger::STDOUT|MyLogger::FILE,string)

  @lastrun_seq[@seq] = @work.seq - 1
  @seq+=1

 end

 def to_s
   "Optimizer"
 end

end
