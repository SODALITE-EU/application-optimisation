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


# Controls Scenario runs
class Scenarios

 def initialize(control,config,optimizer)
  # get references 
  @control = control
  @config = config
  @opt = optimizer
  @seq = 0
  @scenario_params=Array.new
 end

 def scenario_params
  @scenario_params
 end 

 def run(do_opt)

  # Store the current scenorio parameter state in this Hash
  sparam_value=Hash.new
  sparams = @config.sparams

  if sparams.size==1
   sparams.each { |name,p|
       p.value.each { |v| 
                      sparam_value[name]=v 
                      @scenario_params.push(Hash[sparam_value])}
     }  
  elsif @config.global.tune.scenario_params_combiner == "tuples"

   for i in 0..@config.params[sparams.values[0].name].nvalues-1
     sparams.each { |name,p|
        sparam_value[name]=@config.params[name].value[i] 
      }
     @scenario_params.push(Hash[sparam_value])
   end

  elsif @config.global.tune.scenario_params_combiner == "combinations"

   # Calculate left counts of parameter values as we scan parameters
   sp_sizes=Array.new
   sp_products=Array.new
   for i in 0..sparams.size-1
     sp_sizes[i]=@config.params[sparams.values[i].name].nvalues
#     print "#{i} #{sp_sizes[i]}\n"
     if (i==0)
       sp_products[i]=sp_sizes[i]
      else
       sp_products[i]=sp_sizes[i]*sp_products[i-1]
      end
    end
    # Now work across each cobination choosing from values
    for k in 0..sp_products[sparams.size-1]-1
     # string="  Combination #{k}: "
     for i in 0..sparams.size-1
       if (i==0)
         ipos = k % sp_sizes[i]
        else
         ipos=( k / sp_products[i-1] )% sp_sizes[i]
        end
     #  puts " #{sparams[i]}= #{@config.params[sparams[i]].value[ipos]}"
        sparam_value[sparams.values[i].name]=@config.params[sparams.values[i].name].value[ipos]
       end
      @scenario_params.push(Hash[sparam_value])
     end

  end

 nscenarios = @scenario_params.size

 str = "\nWe have #{nscenarios} scenarios...\n\n"
 $log.message(MyLogger::STDOUT|MyLogger::FILE,str)

 str = ""
 for i in 0..@scenario_params.size-1
   str << "  Scenario #{i}\n   "
   @scenario_params[i].each { |n,v|
     str << " #{n}=#{v}"
    }
   str << "\n"
  end
 $log.message(MyLogger::STDOUT|MyLogger::FILE,str)

 return if !do_opt

 # Now we need to run each scenario 
 for i in 0..@scenario_params.size-1
   set_scope(@scenario_params[i])
   str = "\n\nScenario #{i}\n\n "
   @scenario_params[i].each { |n,v|
     str << " #{n}=#{v}"
    }
   str << "\n\n"
   $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
   @opt.run(@scenario_params[i])
   reset_scope
  end

 end

 def set_scope(params)

   @config.params.each { |name,param| 
     if param.instance_variable_defined?("@scenario_scope_expr")
       param.inscope=Param.evalParamExpression(param.scenario_scope_expr,params,@config.params) 
      end
    }

 end 

 def reset_scope

  if (@config.collection.has_key?("SCOPE"))
    @config.params.each { |name,param| param.inscope=false }
    @config.collection["SCOPE"].each { |p| @config.params[p].inscope=true }
   else
    @config.params.each { |name,param| param.inscope=true }
   end

 end

end

