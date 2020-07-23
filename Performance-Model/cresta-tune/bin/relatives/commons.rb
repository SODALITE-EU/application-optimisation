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

require 'pp'

require_relative "commands"
require_relative "metric"
require_relative "sources"

# Standard Class overloads

# Replace with has value if pattern matches key in hash
class String
 def gsub_ifhash(pattern,hash)
    gsub(pattern) do |m|
       if hash.has_key?(m)
         hash[m]
        else
         m
        end
    end
 end
 def gsub_ifhash_t(pattern,hash,types)
    gsub(pattern) do |m|
       if hash.has_key?(m)
         if types.has_key?(m) && types[m]=="label"
           "\"#{hash[m]}\""
          else
           hash[m]
          end
        else
         m
        end
    end
 end
 # as above but ignore quotes
 # types argument is used for labels
 def gsub_ifhash_iq(pattern,hash,types)
    # We need a quote match otherwise use simple method
    if !match(/['"]/)
     return gsub_ifhash_t(pattern,hash,types)
    end
    l=String.new
    quoted_parts=Hash.new
    qp=1
   scan(/((['"])[^\2]+?\2)/).each {|e|
     quoted_parts["@@@#{qp}@@@"]=e[0]
     qp=qp+1
   }
   quoted_parts.each_value {|e|
     l=gsub_ifhash(/#{e}/,quoted_parts.invert)
   }
    l=l.gsub_ifhash_t(pattern,hash,types)
   quoted_parts.each_key {|e|
     l=l.gsub_ifhash(/#{e}/,quoted_parts)
   }
    return l
 end
end

class Hash

  # inclusion test
  def contains?(hash)
   (hash.to_a-to_a).empty?
  end

end

# Class for terminal colours

class Tcolor
  BLACK = 30
  RED = 31
  GREEN = 32
  YELLOW = 33
  BLUE = 34
  MAGENTA = 35
  CYAN = 36
  WHITE = 37
  
 def Tcolor.getCode(s)
  case s
   when "error"
    then RED
   when "warning" 
    then RED
   end
 end


end

# Allow us to use terminal colours in strings

class String
  # ANSI Terminal Escape
  def cescape(code)
    "\e[#{code}m#{self}\e[0m"
  end

  def color(name)
    cescape(Tcolor.getCode(name))
  end

end


# State class handles storing and retrieving run state

class State
 STATEFILE_VERSION=1

 def initialize(file,continue)

  if (continue)
    $log.message(MyLogger::STDOUT|MyLogger::FILE,
                 "Opening state file #{file}")
    @loaded_metrics=Array.new
    begin
      @sfile=File.open(file,'r')
    rescue Exception => e
      $log.message(MyLogger::STDERR|MyLogger::FILE,"Error during open of state file: #{e.message}")
      abort("Cannot continue")
    end
    while line = @sfile.gets
      if (/Run\s+(\d+).*metric\s+(\S+)/=~line)
        $log.message(MyLogger::STDOUT|MyLogger::FILE,
                     " LOADED STATE Run #{$1} metric #{$2}\n")
        @loaded_metrics[$1.to_i]=$2
       end
     end    
    $log.message(MyLogger::STDOUT|MyLogger::FILE,"Closing state file\n")
    @sfile.close
   end

  @sfile=File.open(file,'w')
  t=Time.now
  @sfile.puts("AUTOTUNER State Dump, version #{STATEFILE_VERSION}")
  @sfile.puts("Dump on #{t.localtime}")
  
 end

 def log_state(msg)
  @sfile.puts(msg)
 end

 def loaded_metrics
  @loaded_metrics
 end

end

# Logger class to direct messages to output streams or a log file

class MyLogger
 STDOUT=0b0001
 STDERR=0b0010
 FILE=0b00100

 def initialize(colour)
  @colour = colour
 end

 def logfile(file)
  @logfile = file
 end

 def message(dest,s)

   puts s if (dest & STDOUT) > 0

   if (dest & STDERR) > 0
    if (@colour)
      $stderr.puts s.color("warning")
     else
      $stderr.puts s
     end
   end

   if ( dest & FILE ) > 0
     if (! @file_opened)
      if ! instance_variable_defined?("@lfile")
       @lfile=File.open(@logfile,'w')
      end
      end
           
     @lfile.puts(s) if instance_variable_defined?("@lfile")
     @lfile.flush
    end 

 end

end

class Global
 attr_accessor :use_state, :state_file, :logfile
  @@logfile_default="tune.log";

 def initialize
  @tune=Tune.new
  @src=Sources.new
  @logfile=@@logfile_default
 end

 def tune
  @tune
 end

 def src
  @src
 end

 def to_s
   "global config\n  
  DSL Sources\n
 #{@src}
  Tune settings\n\n #{@tune}\n"
 end

end

# Print summary of results
# Note that this class uses the fact that each scenarios run history
# is recorded by the optimizer
# We later added the option to directly get scenario parameter information

class OPrettyPrint
  CSV=","
  Q='"'

  def initialize(scenarios,opt,param_types,target,show_validation)
   @opt = opt
   @scenarios = scenarios
   @csize=Hash.new
   @header=Array.new
   @tag=Array.new     # for optimizer result code
   @dtag=Array.new    # for default runs
   @param_types=param_types
   @target=target     # tune target (min,max)
   @show_validation=show_validation 
   @csv_mode=false    # Are we doing csv to a file
   @sep=""
   @q=""
   @nparams_table=0   # number of parameters in output table
  end

  def set_mode(mode)
   if mode=="csv"
     @csv_mode = true
     @sep=CSV
     @q=Q
    else
     @csv_mode = false
     @sep=""
     @q=""
    end
   end
    
  def output_csv(file,header)

     set_mode("csv")
     begin
      @file_csv=File.open(file,'w+')
     rescue Exception => e
       $log.message(MyLogger::STDERR|MyLogger::FILE,"Error during open of file during CSV export, abandoning export: #{e.message}")
       return
     end

    $log.message(MyLogger::FILE,"File #{file} opened for csv export")

    header.each_line do |line|
      line.chomp!
      @file_csv.puts("#{@q}#{line}#{@q}\n")
     end

    output

    @file_csv.close

    set_mode("text")

  end

  def route_output(s)

   if @csv_mode
     @file_csv.puts(s)
    else
     $log.message(MyLogger::STDOUT|MyLogger::FILE,s)
    end

  end
  
  def output

    str = "\n#{@q}Optimizer runs summary#{@q}\n\n"
    route_output(str)

     for i in 0..@opt.num_calls-1

       # From AL - check if redundant from loop above
       if @opt.work.run_params.size==0
         next
       end

       @tag.clear
       @dtag.clear
       rstart=@opt.firstrun_seq[i]
       rend=@opt.lastrun_seq[i]
    
       bestpos = @opt.work.bestrun_range(@opt.firstrun_seq[i],@opt.lastrun_seq[i])
       @tag[bestpos]="M"
       @tag[@opt.optimized_run_id[i]]="O"

       if @opt.default_params_run_id[i] < 0
         worstpos = @opt.work.worstrun_range(@opt.firstrun_seq[i],@opt.lastrun_seq[i])
         @dtag[ worstpos ] = "m"
         dmetric = @opt.work.metric[worstpos]
        else   
         @dtag[ @opt.default_params_run_id[i] ] = "d"
         dmetric = @opt.work.metric[@opt.default_params_run_id[i]]
        end

       setup_columns(i)  # note, this sets nparams_table

       if @csv_mode
         str = "#{@q}Scenario#{@q}#{@sep}#{i}#{@sep}#{@q}runs #{rstart}-#{rend}#{@q}\n\n"
        else
         if @scenarios
           str = " Scenario #{i}: runs #{rstart}-#{rend} \n\n"
          else
           str = " Single tune: runs #{rstart}-#{rend} \n\n"
         end
        end 

       if @scenarios
         str_sp = ""
         if @csv_mode
           str_sp = "#{@q}Parameters#{@q}\n\n"
           @scenarios.scenario_params[i].each { |n,v|
            str_sp << "#{@sep}#{@q}#{n}#{@q}"
           }
            str_sp << "\n"
           @scenarios.scenario_params[i].each { |n,v|
            str_sp << "#{@sep}"
            str_sp << "#{@q}" if @param_types[n]=="label"
            str_sp << "#{v}"
            str_sp << "#{@q}" if @param_types[n]=="label"
           }
           str_sp << "\n"
           str << str_sp 
          else
           @scenarios.scenario_params[i].each { |n,v|
            str_sp << " #{n}=#{v}"
           }
           str <<   " Parameters:#{str_sp}\n"
          end
         str << "\n"
        end

       for col in 0..@header.size-1
        if @csv_mode
          str << "#{@sep}#{@q}#{@header[col]}#{@q}"
         else  
          str << " " << sprintf("%*s",@csize[@header[col]],@header[col]);
         end
       end

       if !@csv_mode
       # header separator
       str << "\n" << " " << "-"*(@csize[@header[0]]+@csize[@header[1]]+@csize[@header[2]]+2) << " "
       for col in 3..@nparams_table+2
         str << "-"*@csize[@header[col]]
        end
       str << "-"*(@nparams_table-1) << " "
       str << "-"*5 << "-"*(@csize["metric"]+1)
       str << "-"*(@csize["Validation"]+1) if @show_validation 
       end
       route_output(str)
       str = ""

       if @csv_mode
         for r in rstart..rend
           str << "#{@sep}#{@q}#{@tag[r]}#{@q}"
           str << "#{@sep}#{r}"
           str << "#{@sep}#{@q}#{@dtag[r]}#{@q}"
           for col in 3..@nparams_table+2
            str << "#{@sep}"
            str << "#{@q}" if @param_types[@header[col]]=="label"
            str << "#{@opt.work.run_params[r][@header[col]]}"
            str << "#{@q}" if @param_types[@header[col]]=="label"
            end
           str << "#{@sep}#{ratio(dmetric,@opt.work.metric[r])}"
           str << "#{@sep}#{@opt.work.metric[r].to_s}"
           if @show_validation
             if @opt.work.validation_value[r]
               vstr= @opt.work.validation_value[r]
              else
               vstr= @opt.work.validation_status[r]
              end
             str << "#{@sep}#{vstr}"
            end
           str << "\n"
          end
        else
         for r in rstart..rend
           str << " " << sprintf("%*s",@csize[@header[0]],@tag[r])
           str << " " << sprintf("%*s",@csize[@header[1]],r)
           str << " " << sprintf("%*s",@csize[@header[2]],@dtag[r])
           for col in 3..@nparams_table+2
            str << " " << sprintf("%*s",@csize[@header[col]],@opt.work.run_params[r][@header[col]]);
            end
           str << " " << ratio_s4(dmetric,@opt.work.metric[r])
           col=@nparams_table+2 +2
           
#           str << " " << @opt.work.metric[r].to_s
           str << " " << sprintf("%*s",@csize[@header[col]],@opt.work.metric[r].to_s)
           if @show_validation
             if @opt.work.validation_value[r]
               str << " " << @opt.work.validation_value[r]
              else
               str << " " << @opt.work.validation_status[r]
              end
            end
           str << "\n"
          end
         end
       route_output(str << "\n")

       bestpos = @opt.work.bestrun_range(@opt.firstrun_seq[i],@opt.lastrun_seq[i])
       if !@csv_mode
       str= "  Run #{bestpos} was the best with metric #{@opt.work.metric[bestpos]}\n" 
       route_output(str << "\n")
       end

      end
 
  end

 def setup_columns(i)

  rstart=@opt.firstrun_seq[i]
  rend=@opt.lastrun_seq[i]
  @header.clear
  @header[0]="T"
  @nparams_table = @opt.work.run_params[i].size
  @header[1]="Run"
  @header[2]="M"

  # With scenarios don't put scenario params in text table
  # and alway order scenarios first
  if @scenarios 
   if @csv_mode
     @header+=@opt.work.run_params[i].keys.select { |k|
       @scenarios.scenario_params[i].has_key?(k)
      }
     @header+=@opt.work.run_params[i].keys.select { |k|
       !@scenarios.scenario_params[i].has_key?(k)
      }
    else
     @header+=@opt.work.run_params[i].keys.select { |k|
       !@scenarios.scenario_params[i].has_key?(k)
      }
     @opt.work.run_params[i].each_key { |k|
       if  @scenarios.scenario_params[i].has_key?(k)
         then
          @nparams_table += -1
         end
      }
    end
  else
   # Sort these alphabetically (would not be deterministic before
   # ruby 1.9.2 in any case)
   @header+=@opt.work.run_params[i].keys.sort
  end

  if @target=="max"
    @header.push( "m/m_d" )
   else
    @header.push( "m_d/m" )
   end
  @header.push( "metric" )

  @header.push( "Validation" ) if @show_validation

  # Can't just do headers here because r loop below is over all params
  @header.each { |h| @csize[h]=h.length }
  @opt.work.run_params[i].each { |h,v| @csize[h]=h.length }
  @csize[@header[1]]=[@header[1].length,rend.to_s.length].max

  # Update column widths based on data in rows 
  for r in rstart..rend
    @opt.work.run_params[r].each { |p,v| 
       @csize[p]=[@csize[p],v.to_s.length].max 
    }
    @csize["metric"]=[@csize["metric"],@opt.work.metric[r].to_s.length].max
   end

 end

 # Return metric ratio in 4
 def ratio_s4(m_d,m)

  if @target == "max"
    return "    " if m_d==0.0
    r = Metric.op(m,m_d,"/")
   else
    return "    " if m==0.0
    r = Metric.op(m_d,m,"/")
   end

  return " 100+" if (r >= 100.0)
  return "<0.01" if (r < 0.01)
  sprintf("%5.2f",r);

 end

 # Return metric ratio for csv format
 def ratio(m_d,m)

  if @target == "max"
    return "    " if m_d==0.0
    r = Metric.op(m,m_d,"/")
   else
    return "    " if m==0.0
    r = Metric.op(m_d,m,"/")
   end

   return "#{r}"


 end

end

