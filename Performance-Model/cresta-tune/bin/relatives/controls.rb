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

# Overall control information is held here
class Control
 attr_accessor :do_build, :do_run, :do_opt, :verbose, 
  :save_state, :continue, :continue_seq, :cfile, :validating, 
  :show_validation, :run_independence, :colour, :colour_mode, 
  :parallel, :csv, :csvfile, :strip_dsl
 
 def initialize
  @do_run=true
  @do_build=true
  @do_opt=true
  @strip_dsl=false
  @verbose=false
  @continue=false
  @save_state=false
  @validating=false
  @show_validation=false
  @parallel=false
  @run_independence=1
  @colour=false
  @colour_mode="on black"
  @csv = false
 end

 def to_s
   "Overall control options:
   
      cfile           #{@cfile}
      do_build        #{@do_build} 
      do_run          #{@do_run} 
      verbose         #{@verbose} 
      save_state      #{save_state}
      continue        #{continue} 
      continue_seq    #{continue_seq}
      validating      #{validating}
      show_validation #{show_validation}\n"
 end

end

def print_usage

puts "usage: tune [-help|-h] [-nobuild] [-norun] [-continue seq] [-sv] cfile

  Arguments

   -help          Print this usage information
   -nobuild       Progress without executing the build command (for testing)
   -norun         Progress without executing the run command (for testing)
   -noopt         Do not run the optimizer
   -stripdsl      Parse DSL files removing DSL, do not run optimizer.
   -continue seq  Continue a previous run from the seq'th run
   -colour        Colorize standard output (at present just red for warnings)
   -csv    file   Send summary output to file in csv format
   -sv            Show validation state/value in results table
   cfile          Name of the tuning configuration file

  Description

   This tune script can build and run an application while varying a
   set of tuning parameters that affect the runtime performance.  It
   then determines the best set of tuning parameters.
   The supplied configuration file controls the tuning process.
   As the process progresses status is reported on standard output and
   to a log file (default name tune.log).

   Optionally a record of the run can be kept and this can be used to
   continue a previous run by using the -continue option.

   Results are summarized in a table with the following headers

    T      Indicates optimizer info 
             O indicates this run chose the best parameter values
             M indicates this run had the best metric 
             These can be different for independent metric tuning based
             on run variations
    Run    The id of each run
    M      Indicates which metric was used for the metric ration column
             d  indicates that a run with default parameters was used
             m  indicates that the worst run was used
    params The next columns show the parameter choices per run
    ratio  This column proves a metric ratio for the run 
    metric The metric for the run

  Limitations

   This is a mockup implementation for research purposes and is not
   production code and as such has limited error handling.
   
"
end

# Get controls from command like arguments
def parse_args(control)

 lasta = ""
 ARGV.each do|a|
   if (a == "-nobuild")
    control.do_build=false
   elsif (a == "-help" || a == "-h" )
    print_usage
    exit 0
   elsif (a == "-norun")
    control.do_run=false
   elsif (a == "-noopt")
    control.do_opt=false
   elsif (a == "-v")
    control.verbose=true
   elsif (a == "-d")
    $debug = true
   elsif (a == "-stripdsl")
    control.strip_dsl=true
    control.do_opt=false
   elsif (a == "-parallel")
    control.parallel=true
   elsif (a == "-sv")
    control.show_validation=true
   elsif (lasta == "-continue")
    control.continue=true
    control.continue_seq = a.to_i 
   elsif (lasta == "-csv")
    control.csv = true
    control.csvfile = a
   elsif (a == "-color" || a == "-colour")
    control.colour = true
   elsif (a == "-colorw" || a == "-colourw")
    control.colour = true
    control.colour_mode = "on white"
   else
    # This has to be the last one in the list to overwrite other optoins
    control.cfile = a
   end
   lasta = a
  end

end

