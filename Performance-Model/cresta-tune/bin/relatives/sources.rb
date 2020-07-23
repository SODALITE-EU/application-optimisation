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

require_relative "param"

# Handle parsing on DSL in source

class Sources
 attr_accessor :dsl_filelist, :dsl_filenames_file, :dsl_map_input, :dsl_map_output
 DEFAULT_SENTINEL_MATCH=/\A\s*\!tune\$\s+|\A#pragma\s+tune\s+/

 def initialize
  @files_in=Array.new
  @files_out=Array.new
  @nfiles=0
  @sentinels=Array.new
  @dsls=DEFAULT_SENTINEL_MATCH
  @param_default_values=Hash.new
  @parse_mode="parse"
  @active=false
 end

 def activate
  @active=true
 end

 def active?
  @active
 end

 #because it is a pain to pass this in the constructor
 def setconfig(config)
  @config = config
  @params = config.params
 end

 def store_param_defaults(params)
   params.each { |name,param| @param_default_values[name]=param.default }
 end

 def loadfnames
  @dsl_map_input.sub!("%","(.*)")
  if instance_variable_defined?("@dsl_filelist")
   @dsl_filelist.each { |f| 
            @files_in.push(f)
            pc=f.match(@dsl_map_input)[1]
            @files_out.push(@dsl_map_output.sub("%",pc))
            if (@files_in[@nfiles] == @files_out[@nfiles])
             abort "DSL file mapping error, filenames are the same! abort"
            end
            @nfiles+=1

     }
   elsif instance_variable_defined?("@dsl_filenames_file")
     begin
      ffile=File.open(@dsl_filenames_file,'r')
     rescue Exception => e
       $log.message(MyLogger::STDERR|MyLogger::FILE,"Error during open of dsl filenames file: #{e.message}")
       abort("Cannot continue!")
     end
     while line = ffile.gets
       next if /\A\s*!|\A\s*\Z/=~line
       fmatches=line.scan(/"[^"]+"|'[^']+'|[^,\s]+/)
       fmatches.each{|v| v.gsub!(/\A["']|["']\Z/, '') }
       nmatch=fmatches.size
       @files_in.push(fmatches[0])
       if nmatch>1
        @files_out.push(fmatches[1])
       end
       @nfiles+=1
     end
     ffile.close
     if nmatch==1
      @files_in.each { |f| 
            pc=f.match(@dsl_map_input)[1]
            fout=@dsl_map_output.sub("%",pc)
            @files_out.push(fout)
            if (f == fout)
             abort "DSL file mapping error, filenames are the same! abort"
            end
       }
      end

   end
  end

  # prescan files for DSL definitions   
  def prescan(strip_dsl)
   @strip_dsl = strip_dsl
   @parse_mode="prescan"
   parse(@param_default_values)
   @parse_mode="parse"
   @strip_dsl=false
  end

  # Parse each file for DSL and rewrite this should happen on a rebuild
  def parse(param_values)

   param_values_inscope=Hash.new

   $log.message(MyLogger::STDOUT|MyLogger::FILE,"Starting DSL file parsing")
  
   for i in 0..@nfiles-1
     if @strip_dsl
       str = " Stripping DSL from file #{@files_in[i]} -> #{@files_out[i]}\n"
      else
       str = " Parsing file #{@files_in[i]} -> #{@files_out[i]}\n"
      end
     $log.message(MyLogger::FILE,str)
     begin
      fin=File.open(@files_in[i],'r')
      fout=File.open(@files_out[i],'w+')
     rescue Exception => e
       $log.message(MyLogger::STDERR|MyLogger::FILE,"Error during open of file during DSL parsing phase: #{e.message}")
       abort("Cannot continue!")
     end

     param_values_inscope.clear
     state="start"
     while line = fin.gets

       line.chomp!  
       if m=@dsls.match(line)
         dsl=m.post_match
         str="  DSL at line.#{fin.lineno}: #{dsl}"

         next if @strip_dsl
         # Handle if (expr) clause
         if /if\s*\(\s*(.*?)\s*\)\s*(.*)/=~dsl
           dsl=$2
           if_expr_value=Param.evalParamExpression($1,param_values_inscope,@params)
           str2 = str << "\n         line.#{fin.lineno}: if (#{$1}) -> #{if_expr_value}"
           if ! if_expr_value 
             $log.message(MyLogger::FILE,str2 << "\n")
             next
            end
          end

         if /param\s+define\s+(\w+)\s+type\s+(int|real|label)\s+range\s+(.+)\s*/=~dsl
           name=$1
           values=$3
           if @parse_mode == "prescan"
             param=Param.new(name,$2)
             @params[name]=param
             @config.param_types[name]=$2
             if (values=~/\s*(.*)\s+default\s+(.+)\s*/)
               param.range=$1
               param.default=$2
              else
               param.range=values
              end
             param.createvalues
             param_values_inscope[name]=@params[name].default
           else
             param_values_inscope[name]=param_values[name]
           end
          fout.puts( line << "\n")
         # Now parameter constrint ( gp = lexpr ) 
         elsif /param\s+define\s+(\w+)\s+type\s+(int|real|label)\s+constraint\s+(.+)\s*/=~dsl
           name=$1
           gen=$3
           if @parse_mode == "prescan"
             param=Param.new(name,$2)
             @params[name]=param
             @config.param_types[name]=$2
             if (gen=~/\s*=\s*([^=].*\Z)/)
                param.generator="constraint"
                param.expression=$1
              else
               abort "bad syntax for constraint"
              end
             cexpr = Param.evalParamExpression(param.expression,param_values_inscope,@params)
             cexpr = cexpr.to_i if param.type == "int"
             param_values_inscope[name]=cexpr
           else
             param_values_inscope[name]=param_values[name]
           end
          fout.puts( line << "\n")
         # General constraint
         elsif /param\s+constraint\s+(.+)\s*/=~dsl
           @config.constraints.push($1)
           fout.puts( line << "\n")
         elsif /param\s+import\s+(.*)/=~dsl
           $1.split(/[ ,]/).each {|p| 
              param_values_inscope[p.strip]=param_values[p.strip]
             }
           fout.puts( line << "\n" )
         elsif /(inject|inject_r|inject_r\$)\s*:(.*)/=~dsl
           code=$2
           if $1 == "inject"
             fout.puts( code << "\n" )
           elsif $1 == "inject_r"
             code=code.gsub_ifhash_iq(/([A-Za-z_]+[0-9]*[A-Za-z]*)/,param_values_inscope,@config.param_types)
             fout.puts( code << "\n" )
           elsif $1 == "inject_r$"
             param_values_inscope.each {|p,v|
                if code=~/(\$\{#{p}\})/
                  code=code.gsub("\$\{#{p}\}","#{v}")
                 elsif code=~/(\$#{p})/
                  code=code.gsub("\$#{p}","#{v}")
                 end
              }
             fout.puts( code << "\n" )
           end

         elsif /begin\s+replace/=~dsl
            fout.puts( line << "\n" )
            $log.message(MyLogger::FILE,str << "\n")
            scope_loop(fin,fout,"replace",param_values_inscope)
            next

         elsif /begin\s+skip/=~dsl
            if /skip\s+fill/=~dsl
              mode="skip fill"
             else
              mode="skip"
             end
            fout.puts( line << "\n" )
            $log.message(MyLogger::FILE,str << "\n")
            scope_loop(fin,fout,mode,param_values_inscope)
            next
         else
           str << "\n         line.#{fin.lineno}: DSL not recognized, ignored"
          
         end

         $log.message(MyLogger::FILE,str << "\n")
         next
       end

      fout.puts(line << "\n")
    
     end

     fin.close
     fout.close
   end
  
   $log.message(MyLogger::STDOUT|MyLogger::FILE,"...DSL file parsing done\n")


  end

# We do this for actions bounded with scope (begin, end)
  def scope_loop(fin,fout,action,param_values_inscope)

   while line = fin.gets

     line.chomp!  
     if m=@dsls.match(line)
       dsl=m.post_match
       str="  DSL at line.#{fin.lineno}: #{dsl}"
       if /end\s+skip/=~dsl
         fout.puts( line << "\n" )
         if action=="skip" || action=="skip fill"
          $log.message(MyLogger::FILE,str << "\n")
          return
         end
       end
       if /end\s+replace/=~dsl
         fout.puts( line << "\n" )
         if action=="replace" 
          $log.message(MyLogger::FILE,str << "\n")
          return
         end
       end

     else
      if action=="replace"
        code=line.gsub_ifhash_iq(/([A-Za-z_]+[0-9]*[A-Za-z]*)/,param_values_inscope,@config.param_types)
        fout.puts( code << "\n" )

      end
      if action=="skip fill"
        fout.puts( "\n" )      
      end
     end

   end

  end


  def to_s

   if @active
     str = "  DSL Source mappings for #{@nfiles} files\n\n"
     for i in 0..@nfiles-1
       str << "    #{@files_in[i]} -> #{@files_out[i]}\n"    
     end
    else
     str = "  No DSL source configured\n"
    end

   return str
  end

end

