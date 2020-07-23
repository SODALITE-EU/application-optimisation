#!/usr/bin/ruby
#
# Autotuner Mockup Driver
#
# Harvey Richardson Cray UK 2013-2014, 2016, 2017
#
# Copyright (C) 2013-2017 Cray UK Ltd
# License: Not licensed, CRESTA partner internal use only
#
#

require_relative "metric"

# Container for list of runs to do in a batch
# The current set of runs (in run_params) is indexed from @seq_start to @seq-1
class Worklist
 attr_accessor :seq

 def initialize(control,config)
  @control = control
  @config = config
  @seq=0
  @seq_start=0
  @run_params=Array.new
  @metric=Array.new
  @validation_status=Array.new
  @validation_value=Array.new
  @repeat_metric=Array.new
  @runtime=Array.new
  @requires_build=Array.new
  @special_replacments=Hash.new
 end

 def pushrun(hash)
  @run_params.push(Hash[hash])
  @requires_build[@seq]=false
  if (! @config.collection.has_key?("BUILD"))
    @requires_build[@seq]=true
   elsif (@seq == 0)
    @requires_build[@seq]=true
   else
    @config.collection["BUILD"].each { |p|
      p.split(/[ ,]/).each { |k|
      if (@run_params[@seq-1][k] != @run_params[@seq][k] )
        @requires_build[@seq]=true
       end
       }
     }
   end
  @seq=@seq+1
 end

 def execute
  str = "Starting executions for current parameter search"
  print "seq_start #{@seq_start} seq #{@seq}\n" if $debug
  $log.message(MyLogger::STDOUT|MyLogger::FILE,str)
  i=@seq_start
  while i<@run_params.size do
    build_tag="tag#{i}"
    # We also need to do a build if we have been continuing from state
    if @requires_build[i] || (@control.continue && @control.continue_seq == i)
      puts "Command string is #{@config.build.command}\n" if $debug
      command=@config.build.command
      @run_params[i].each {|p,v| 
         if v != "unset" && command=~/(\$\{#{p}\})/
           command=command.gsub("\$\{#{p}\}","#{v}")
          elsif v != "unset" && command=~/(\$#{p})/
           command=command.gsub("\$#{p}","#{v}")
          end
       }
      p="build_tag"
      if command=~/(\$\{#{p}\})/
        command=command.gsub("\$\{#{p}\}","#{build_tag}")
       elsif command=~/(\$#{p})/
        command=command.gsub("\$#{p}","#{build_tag}")
       end
      if (@config.build.instance_variable_defined?("@param_file") )
        pfile=@config.build.param_file
        p="build_tag"
        if pfile=~/(\$\{#{p}\})/
          pfile=pfile.gsub("\$\{#{p}\}","#{build_tag}")
         elsif pfile=~/(\$#{p})/
          pfile=pfile.gsub("\$#{p}","#{build_tag}")
         end
        File.open(pfile,"w"){ |f|
          @run_params[i].each {|p,v| 
             f.write("#{p} #{v}\n") if v != "unset"
           }    
         }
       end

      # If we are using previous state for the metric then don't
      # do a build

      if !@requires_build[i] 
        msg = "Build Required as this is the first run after using state data "
        $log.message(MyLogger::STDOUT|MyLogger::FILE,msg)
      end
 
      if @control.continue && @control.continue_seq > i
        msg = "(build not needed, have state)"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,msg)
      elsif (@control.do_build )

        if (@config.global.src.active?)
          @config.global.src.parse(@run_params[i])
         end
        msg = "Executing build command #{command}"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,msg)

        output=`#{command} 2>&1`
        $log.message(MyLogger::FILE,output)
        if ($?.to_i > 0)
         $log.message(MyLogger::STDERR,"WARNING: Build returned non-zero exit code, see log")
         $log.message(MyLogger::FILE,"WARNING: Build process exited with non-zero error code: #{$?}")
        end

       else
        msg = "(build disabled) build command #{command}"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,msg)
       end

     end

    repeating = @config.global.tune.nrepeats > 1
    for ir in 1..@config.global.tune.nrepeats

      command=@config.run.command
      @run_params[i].each {|p,v| 
        if v != "unset" && command=~/(\$\{#{p}\})/
          command=command.gsub("\$\{#{p}\}","#{v}")
         elsif v != "unset" && command=~/(\$#{p})/
          command=command.gsub("\$#{p}","#{v}")
         end
       }

      # This is where we rewrite the run command with the special
      # variables that can be used (run_id, build_id, repeat_id ... )
      special_replacements = Hash["build_tag"=> build_tag, "run_id" => i] 
      if (repeating)
        special_replacements["repeat_id"] = ir
       end
      special_replacements.each{ |p,v|
        if command=~/(\$\{#{p}\})/
          command=command.gsub("\$\{#{p}\}","#{v}")
         elsif command=~/(\$#{p})/
          command=command.gsub("\$#{p}","#{v}")
         end
       }

      # If RUN_ENVARS set then use env to place values in envars during run
      if ( @config.collection.has_key?("RUN_ENVARS"))
        precmd=""
        @config.collection["RUN_ENVARS"].each { |p|
          p.split(/[ ,]/).each { |k|
            if (run_params[i].include?(k))
              command = "export #{k}=#{run_params[i][k]}; #{command}"
              precmd = ""
             end
           }
         }
        command = "#{precmd}#{command}"
      end

      if (@config.run.instance_variable_defined?("@param_file") )
        pfile=@config.run.param_file
        p="run_id"
        if pfile=~/(\$\{#{p}\})/
          pfile=pfile.gsub("\$\{#{p}\}","#{i}")
         elsif pfile=~/(\$#{p})/
          pfile=pfile.gsub("\$#{p}","#{i}")
         end
        File.open(pfile,"w"){ |f|
          @run_params[i].each {|p,v| 
             f.write("#{p} #{v}\n") if v != "unset"
           }    
         }
       end
      if (repeating)
        msg = "Executing Run #{i}, repeat #{ir}, command: #{command}"
       else
        msg = "Executing Run #{i}, command: #{command}"
       end
      $log.message(MyLogger::STDOUT|MyLogger::FILE,msg)
      t1=Time.now.to_f
  
      have_metric = @control.continue && @control.continue_seq > i
      if (have_metric)
        $log.message(MyLogger::STDOUT|MyLogger::FILE,
                     "Run not required as we have state information")
     
      elsif (@control.do_run)
        output=`#{command} 2>&1`
        $log.message(MyLogger::FILE,output)
        if ($?.to_i > 0)
         $log.message(MyLogger::STDERR,
          "WARNING: Run returned non-zero exit code, see log")
         $log.message(MyLogger::FILE,
          "WARNING: Run process exited with non-zero error code: #{$?}")
         end
       else
        output="(run disabled) #{command}"
        $log.message(MyLogger::STDOUT|MyLogger::FILE,output)
       end
      t2=Time.now.to_f
      t=t2-t1
      @runtime[i]=t

      # Get validation state
      if (@control.validating)
        if @config.run.validation_source == "stdout"
          vstate, vvalue, vmetric = Validation.fromString(output)
         end
        if @config.run.validation_source == "command"
          vcommand = @config.run.validation_command
          special_replacements.each{ |p,v|
            if vcommand=~/(\$\{#{p}\})/
              vcommand=vcommand.gsub("\$\{#{p}\}","#{v}")
             elsif vcommand=~/(\$#{p})/
              vcommand=vcommand.gsub("\$#{p}","#{v}")
             end
           }
          $log.message(MyLogger::FILE|MyLogger::STDOUT,"Validating with command #{vcommand}")
          val_output=`#{vcommand} 2>&1`
          $log.message(MyLogger::FILE,val_output)
          vstate, vvalue, vmetric = Validation.fromString(val_output)
         end
        if vstate != "validated"
          message="Run #{i} validation failed: #{vstate}"
          $log.message(MyLogger::STDERR|MyLogger::FILE,message)
          if @config.run.validation_failure_mode == "abort"
            $log.message(MyLogger::FILE,"*** ABORT due to validation failure")
            abort("ABORTING due to valudation failure for run #{i}")
           end
         end
        @validation_status[i] = vstate
        @validation_value[i] = vvalue
        # What if we picked up a metric
        if ! vmetric.nil? 
          if @config.global.tune.metric_placement != "validation"
            $log.message(MyLogger::STDERR|MyLogger::FILE,"Warning: metric defined in validation but metric source is set to #{@config.global.tune.metric_placement}")
           end
         end
       end
      # Now set the metric
      if (have_metric)
        @metric[i] = $state.loaded_metrics[i]
       elsif !vmetric.nil?
        @metric[i] = vmetric
       else
        if (@config.global.tune.metric_placement == "lastregexp")
           regexp = Regexp.new(@config.global.tune.metric_regexp)
          else
           regexp = nil
          end
        @metric[i] = case @config.global.tune.metric_source
          when "runtime" 
            then @runtime[i]
          when "stdout" 
            then Metric.fromString(output,regexp)
          when "file"
            then 
              mfile=@config.global.tune.metric_file
              special_replacements.each{ |p,v|
                if mfile=~/(\$\{#{p}\})/
                  mfile=mfile.gsub("\$\{#{p}\}","#{v}")
                 elsif mfile=~/(\$#{p})/
                  mfile=mfile.gsub("\$#{p}","#{v}")
                 end
               }
             Metric.fromFile(mfile,regexp)
         end
        if (repeating)
          if (ir == 1)
            @repeat_metric[i]=Array.new(@config.global.tune.nrepeats)
           end
          @repeat_metric[i][ir-1]=@metric[i]
         end
       end
      if (repeating)
        line=sprintf( "Run #{i} repeat #{ir} took %.10fs, metric %s\n",
                      t,@metric[i])
       else
        line=sprintf( "Run #{i} took %.10fs, metric %s\n",t,@metric[i])
       end
      $log.message(MyLogger::STDOUT|MyLogger::FILE,line)

    end

    if (repeating)
      @metric[i]=Metric.aggregate(@repeat_metric[i],
                                  @config.global.tune.metric_aggregation)
      line=sprintf("Run #{i} aggregate metric %s\n",@metric[i])
      $log.message(MyLogger::STDOUT|MyLogger::FILE,line)
     end

    $state.log_state(line) if (@control.save_state)

    # AL    
    if @metric[i].to_s.empty?
      @metric[i]=Float::INFINITY
     end

    i+=1

   end

 end

 def new_sequence
  @seq_start=@seq
 end

 # This is the number of runs in the current sequence (that would be executed)
 def seq_nruns
   return @seq-@seq_start
  end

 # This is the range for the previous execute
 def bestrun
  bestrun_range(@seq_start,@seq-1)
 end

 def bestrun_range(istart,iend)
  i=istart
  metric=@metric[istart]
  im=i
  i+=1
  while i<=iend do
    if( Metric.cmp(@metric[i],metric,@config.global.tune.target))
      metric = @metric[i]
      im = i
     end
    i+=1
   end    
  return im
 end 

 def worstrun_range(istart,iend)
  i=istart
  metric=@metric[istart]
  im=i
  i+=1
  while i<=iend do
    if( !Metric.cmp(@metric[i],metric,@config.global.tune.target))
      metric = @metric[i]
      im = i
     end
    i+=1
   end    
  return im
 end 

 def metric
   @metric
  end

 def validation_status
   @validation_status
  end
 
 def validation_value
   @validation_value
  end
 
 def run_params
   @run_params
  end
 def to_s

  i=@seq_start
  string=""
  while i<@run_params.size do
    if (@requires_build[i])
      string << "  [B]"
     else
      string << "     "
     end
    string << " Run #{i} params:"
    @run_params[i].each {|p,v| string << " #{p}=#{v}"}
    string << "\n"
    i+=1
   end
   return string
 end

end

