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

# Routines to get Validation state
class Validation

 # Return validation output from string with optional metric
 #        optinally return a VALUE that can quantify the validation 
 #        (for example a tolerance)
 # Look for: tune run status STATE [ metric METRIC ]    
 #           tune run validated VALUE [ metric METRIC ] 
 #           tune run validate VALUE [ metric METRIC ]  
 def Validation.fromString(string)

    string.each_line { |s|
      if s=~/tune\s+run\s+status\s+(\S+)\s+metric\s+(\S+)/
       return [ $1, nil, $2 ]
      elsif s=~/tune\s+run\s+status\s+(\S+)/
       return [ $1, nil, nil ]
      elsif s=~/tune\s+run\s+validated\s+(\S+)\s+metric\s+(\S+)/
       return [ "validated", $1, $2 ]
      elsif s=~/tune\s+run\s+validated\s+(\S+)/
       return [ "validated", $1, nil ]
      elsif s=~/tune\s+run\s+validate\s+(\S+)\s+metric\s+(\S+)/
       return [ "validate", $1, $2 ]
      elsif s=~/tune\s+run\s+validate\s+(\S+)/
       return [ "validate", $1, nil ]
      end
     }

     return [ "not found" , nil , nil ]

  end

end


# Holds configuration information about the build
class Build
 attr_accessor :command, :param_file
 @@command_default = "make"

 def initialize
   @command = @@command_default
 end

 def to_s
  string= "command=#{@command}"
  if instance_variable_defined?("@param_file")
    string << "\n param-file=#{@param_file}"  
  end
  return string
 end

end

# Holds configuration information about run

class Run
 attr_accessor :command, :param_file, :validation_source, :validation_command, :validation_failure_mode

 def initialize
  @validation_failure_mode = "abort"
 end

 def to_s
  if @command.lines.count >1
    string = "commands...\n" << @command
   else
    string = "command=#{command}"
   end
  if instance_variable_defined?("@param_file")
    string << "\n param-file=#{@param_file}"  
  end
  return string
 end

end

class Tune
 attr_accessor :mode, :target, :metric_source, :scope, :metric_placement, 
 :metric_file, :metric_regexp, :nrepeats, :metric_aggregation, 
 :scenario_params_combiner
 def initialize
  @mode = "tune"
  @scenario_params_combiner = "combinations"
  @target = "min"
  @metric_source = "runtime"
  @nrepeats = 1
  @metric_aggregation = "target"
 end

 def to_s
  string="  mode           #{@mode}
   scope          "
  string << @scope.join(" ") if !@scope.nil?
  string << "
   target         #{@target} 
   metric-source  #{@metric_source}"
 end

end

