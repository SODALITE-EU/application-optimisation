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

require_relative "commons"
require_relative "commands"
require_relative "param"

class Configuration

  def initialize(control)
   @control = control
   @fname = control.cfile
   @global = Global.new
   @params = Hash.new
   @sparams = Hash.new  # Scenario parameters
   @tparams = Hash.new  # These are tuning parameters
   @gparams = Hash.new  # Generated parameters from "product"
   @cparams = Hash.new  # Generated parameters from constraint expression
   @param_types = Hash.new # Hash of parameter types
   @constraints = Array.new # Logical constraints
   @collection = Hash.new
   @ipool=Array.new
   @build=Build.new
   @run=Run.new

   parsefile()

   # Make sure we have the scenario parameters in collection SCENARIO_PARAMS
   if ( @collection.has_key?("SCENARIO_PARAMS") ) 
     if ( @collection["SCENARIO_PARAMS"].size == 1 ) 
       if (@collection.has_key?(@collection["SCENARIO_PARAMS"][0]) )
          @collection["SCENARIO_PARAMS"]=@collection[@collection["SCENARIO_PARAMS"][0]]
       end
      end

     # Had to do this here becasuse a collection for the scenario parameters
     # could have been defined after we loaded the parameters
     @collection["SCENARIO_PARAMS"].each { |p| @params[p].generator="scenario" }
    end

   update_param_hashes

   end

   def update_param_hashes

   # Fill arrays per parameter type
   @params.each { |name,p| 
     if (p.generator == "scenario")
       @sparams[name]=p
      end
     if (p.generator == "range")
       @tparams[name]=p
      end
     if (p.generator == "product")
       @gparams[name]=p
      end
     if (p.generator == "constraint")
       @cparams[name]=p
      end
    }

  end

  def params
   @params
  end
  def sparams
   @sparams
  end
  def tparams
   @tparams
  end
  def gparams
   @gparams
  end
  def cparams
   @cparams
  end
  def param_types
   @param_types
  end
  def constraints
   @constraints
  end
  def ipool
   @ipool
  end
  def collection
   @collection
  end
  def global
   @global
  end
  def build
   @build
  end
  def run
   @run
  end

# Parse the file for the global configuration
# This is not a proper parser, just based on depth (context variable)
# There will be an XML variant and that will use a proper parser
  def parsefile
    begin
      cfile = File.open(@fname)
    rescue Exception => e
      warning "Error during open of configuration file: #{e.message}"
      abort("Cannot continue")
    end
    context = "top"
    while line = cfile.gets
      # Ignore comments
      next if /\A\s*!|\A\s*\Z/=~line
      line.chomp!
      if (/begin\s+(\w+)/=~line) 
        context = context+"."+$1
        next
       end
      if (/end\s+(\w+)/=~line) 
        context = context.sub /\.\w+$/,""
        next
       end
      if (context == "top.configuration.tune")
        if line =~ /\s*mode:\s*(\w+)/
          @global.tune.mode = $1;
         elsif line =~ /\s*scenario-params:\s*(.*)/
          @collection["SCENARIO_PARAMS"]=$1.split(/[ ,]/).each {|p| p.strip!}  
         elsif line =~ /\s*scenario-params-combiner:\s*(.*)/
          @global.tune.scenario_params_combiner = $1;
         elsif line =~ /\s*scope:\s*(.*)/
          @collection["SCOPE"]=$1.split(/[ ,]/).each {|p| p.strip!}  
          @global.tune.scope=@collection["SCOPE"]
         elsif line =~ /\s*target:\s*(\S+)/
          @global.tune.target = $1;
         elsif line =~ /\s*metric-source:\s*(\S+)/
          @global.tune.metric_source = $1;
         elsif line =~ /\s*metric-placement:\s*(\S+)/
          @global.tune.metric_placement = $1;
         elsif line =~ /\s*metric-regexp:\s*(.*)/
          @global.tune.metric_regexp = $1;
         elsif line =~ /\s*postrun-metric-file:\s*(\S+)/
          @global.tune.metric_file = $1;
         elsif line =~ /\s*run-repeats:\s*(\d+)/
          @global.tune.nrepeats = $1.to_i;
         elsif line =~ /\s*metric-aggregation:\s*(\S+)/
          @global.tune.metric_aggregation = $1;
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
         end
       elsif (context == "top.configuration")
        if line =~ /\s*state-file:\s*(\S+)/
          @global.state_file = $1;
         elsif line =~ /\s*progress-log:\s*(\S+)/
          @global.logfile = $1;
        else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
        end
       elsif (context == "top.sources")
        if line =~ /\s*dsl-filelist:\s*(.*)/
          @global.src.dsl_filelist=$1.split(/[ ,]/).each {|f| f.strip!}
          @global.src.activate
         elsif line =~ /\s*dsl-filenames-file:\s*(\S+)/
          @global.src.dsl_filenames_file=$1
          @global.src.activate
         elsif line =~ /\s*dsl-map-input:\s*(\S+)/
          @global.src.dsl_map_input=$1
         elsif line =~ /\s*dsl-map-output:\s*(\S+)/
          @global.src.dsl_map_output=$1
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
         end
       elsif (context == "top.parameters.typing")
        if line =~ /(\w+)\s+(\w+)/
          type=$1
          name=$2
          if ( "int,real,label" =~ /#{type}/)
           param=Param.new(name,type)
           @params[name]=param
           else
            warning "Invalid parameter typing definition #{type}"
           end
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
         end
       elsif (context == "top.parameters.constraints")
        if line =~ /\s*depends\s+(.+)/
          values=$1
          @ipool.push(values.split(/[ ,]/).each {|p| p.strip!} )
        elsif line =~ /constraint\s+(\w+)\s+inscope\s+(if|forscenario)\s+(.+)\s*/
          name=$1
          lexp=$3
          if $2 == "forscenario"
            @params[name].scenario_scope_expr=lexp
            
          else
            @params[name].scope_expr=lexp
          end
        elsif line =~ /(\w+)\s+(\w+)\s+(.+)/
          constraint=$1
          name=$2
          values=$3
          if ( "constraint,range,default,product,depends" =~ /#{constraint}/)
            if (!@params.has_key?(name))
             warning "Error on line #{cfile.lineno}: parameter #{name} is not previously typed"
             abort "tune run aborted"
            end
            param=@params[name]
            if (constraint == "range")
              if (values=~/\s*(.*)\s+default\s+(.+)\s*/)
                param.range=$1
                param.default=$2
               else
                param.range=values
               end
             elsif (constraint == "product")
               # At the moment only supporting parameters here
               # not the inline {a,b} form
               param.factorstring=values
               param.generator="product"
             elsif (constraint == "constraint")
               # We either have var = expr 
               # or we have     logical_expr
               # we handle these cases respectively below
              if (values=~/\A\s*=\s*([^=].*)/)
                param.generator="constraint"
                param.expression=$1
               else
                @constraints.push("#{name} #{values}")
               end
             elsif (constraint == "default")
              param.default=values
             elsif (constraint == "depends")
#             params are name and values; saves doing this earlier
              params=name+","+values
              @ipool.push(params.split(/[ ,]/).each {|p| p.strip!} )
             end  
           else
            warning "Invalid constraint definition #{line}"
           end
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
         end
       elsif (context == "top.parameters.collections")
        if line =~ /\s*(\w+):\s+(.*)\s*/
          name=$1
          params=$2
          @collection[name]=params.split(/ ,/).each {|p| p.strip!}  
         end
       elsif (context == "top.build")
        if line =~ /\s*command:\s+(.*)\s*/
          @build.command = $1;
         elsif line =~ /\s*param-file:\s+(.*)\s*/
          @build.param_file = $1;
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"

         end
       elsif (context == "top.run")
        if line =~ /^\s*command:\s+(.*)\s*/
          @run.command = $1;
         elsif line =~ /\s*param-file:\s+(.*)\s*/
          @run.param_file = $1;
         elsif line =~ /\s*validation-source:\s+(stdout|command)\s*/
          @run.validation_source = $1;
          @control.validating = true          
         elsif line =~ /\s*validation-command:\s+(.*)\s*/
          @run.validation_command = $1;
         elsif line =~ /\s*validation-failure-mode:\s+(abort|warning)\s*/
          @run.validation_failure_mode = $1;
         elsif line =~ /\s*independence:\s+(\d+)\s*/
          @control.run_independence = $1;
         else
          warning "Error on line #{cfile.lineno}: not expecting text #{line}"
         end
       elsif (context == "top.run.commands")
         # Multiline run command
         if @run.command.nil?
           @run.command = line;
          else
           @run.command << "\n" << line;
          end
       elsif (context == "top.configuration.fred")
         print "Invalid Context (just here to copy and paste next lot)"
       end
     end
     
    cfile.close
  end

  def resolve_dependencies
   # Need to build the full ipools array and pool mappings
   pool_map=Hash.new
   @ipool.each_with_index { |pool,index|
      pool.each { |p| pool_map[p]=index }
   }
   # Now fold in parameters not previously in a pool
    psize=@ipool.size
   # Hashes preserve order after ruby 1.9.2 where we can do @tparams.each
   # @tparams.each_key { |name|
   # Deterministic order
    @tparams.keys.sort.each { |name|
      if (!pool_map.has_key?(name))
        @ipool.insert(-psize,name)
       end
     }
  end

  def to_s
   string="Tuning Configuration:\n\n"
   string << "Loaded from file " << @fname << "\n\n" << @global.to_s << "\n"
   string << "Build config\n " << @build.to_s << "\n\n"
   string << "Run config\n "  << @run.to_s << "\n"
   # Validation
   if (@control.validating)
     string << " Validation enabled from source #{@run.validation_source}\n"
     if @run.validation_source == "command"
       string << " Validation command: #{@run.validation_command}\n"
      end
       string << " Validation failure mode is #{@run.validation_failure_mode}\n"
    end
   if (@global.tune.mode == "tune")
     string << "\nTuning mode is a single tune run" << "\n" 
    else
     string << "\nTuning mode is to tune for scenarios" << "\n" 
    end

   if (@sparams.size >0)

     pl=@sparams.size>1 ? "are":"is"
     string << "\nThere #{pl} #{@sparams.size} scenario parameters\n\n"

     @sparams.each { |name,p| 
       string <<  "  name = " << name << "\n"
       string <<  "         type = " << p.type
       string <<  ", range = " << p.range << "\n"
       if (p.instance_variable_defined?("@default"))
         string <<  "         default = #{p.default}\n"
        end
      }

    end

   pl=@tparams.size>1 ? "are":"is"
   pls=@tparams.size>1 ? "s":""
   string << "\nThere #{pl} #{@tparams.size} tuning parameter#{pls}\n\n"

   @tparams.each { |name,p| 
     string <<  "  name = " << name << "\n"
     string <<  "         type = " << p.type
     string <<  ", range = " << p.range << "\n"
     if (p.instance_variable_defined?("@default"))
       string <<  "         default = #{p.default}\n"
      end
    }

   string << "\n"

   if ( @gparams.size > 0)

     pl=@gparams.size>1 ? "are":"is"
     pls=@gparams.size>1 ? "s":""
     string << "There #{pl} #{@gparams.size} generated parameter#{pls}\n\n"

     @gparams.each { |name,p| 
       string <<  "  name = " << name << "\n"
       string <<  "         type = " << p.type
       string << ", factors = " << p.factorstring << "\n"
      }

     string << "\n"

     end

   if ( cparams.size > 0)

     pl=@cparams.size>1 ? "are":"is"
     pls=@cparams.size>1 ? "s":""
     string << "There #{pl} #{@cparams.size} constraint-generated parameter#{pls}\n\n"

     @cparams.each { |name,p| 
       string <<  "  name = " << name << "\n"
       string <<  "         type = " << p.type
       string << ", expression = " << p.expression << "\n"
      }
     string << "\n"

     end


   if ( @constraints.size > 0)
     pl=@constraints.size>1 ? "are":"is"
     string << "There #{pl} #{@constraints.size} logical constraints\n\n"

     @constraints.each { |exp| 
       string <<  "  constraint: " << exp << "\n"
      }
  
     string << "\n"

     end

   string << "Collections:\n"

   @collection.each { |n,p|
     if ( n != "SCOPE" && n != "SCENARIO_PARAMS")
       string << "  #{n}: " << p.join(" ") << "\n"
      end 
    }

   # independent parameter Exploration
   string <<  "\nDependency groupings\n\n"
   ipool.each { |p|
     string << " "
     if (p.class==String)
       string << " #{p}"
      else
       p.each { |q| string << " #{q}" }
      end
     string << "\n"
    }

   return string

  end   

  def warning(string)
   if @control.colour
     $stderr.puts string.color("warning")
    else
     $stderr.puts string
    end
  end

end

