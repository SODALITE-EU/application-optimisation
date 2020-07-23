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

# The tuning parameter definitions
class Param
 attr_accessor :name, :type, :range, :factorstring, :default, :inscope, 
               :generator, :expression, :scenario_scope_expr, :scope_expr

 def initialize(name,type)
  @name = name
  @type = type
  @inscope = true
  @generator = "range"
  @values_valid = false
 end

 def to_s
   "name=#{@name} type=#{@type} range=#{@range} default=#{default}"
 end

 # Fill in values array and set default if not already set 
 # Need to add support for product here
 # Ranges are: list, m-n,  M:N:K
 def createvalues
   if @values_valid
     return
    end
   if (@range =~ /(\d+)-(\d+)/ )
     @value=Array($1.to_i..$2.to_i)
    elsif (@range =~ /(\d+):(\d+):(\d+)/ )
     @value=Array.new
     r=($1.to_i..$2.to_i).step($3.to_i)
     r.each {|v| @value.push(v)}
    elsif (@range =~ /(\d+):(\d+)/ )
     @value=Array($1.to_i..$2.to_i)
    else
     @value=@range.scan(/"[^"]+"|'[^']+'|[^,\s]+/)
     # Strip containing quotes
     @value.each{|v| v.gsub!(/\A["']|["']\Z/, '') }
    end

   @nvalues=@value.size
   if (!instance_variable_defined?("@default"))
     @default=@value[0]
    end
   @values_valid=true
 end

 def createfactors
   @factors=@factorstring.split("\s").each {|v| v.strip!}  
   @nfactors=@factors.size
 end

 def nvalues
  @nvalues
 end

 def value
  @value
 end

 def nfactors
  @nfactors
 end

 def factors
  @factors
 end

 # Evaluate expression for params
 #  Arguments,  expression, hash of name->value, params hash
 #  Make sure to quote any parameter that should turn into a string
 def Param.evalParamExpression(expr,param_values,params)
   #puts param_values
   cexpr = ""
   expr.scan(/\w+|\W+/){ |s|

     if s=~/\w+/ && param_values.has_key?(s)
#      puts "got word #{s} which is a parameter"
#      puts "#{s} #{params[s].type} value #{param_values[s]}"
       if params[s].type == "label"
         cexpr << '"' << param_values[s] << '"'
        else
         cexpr << param_values[s].to_s
        end
      else
#      puts "ignoring #{s}"
       cexpr << s
      end
     }
#   puts "after loop cexpr=#{cexpr}"
#   puts eval cexpr
   begin  
    eval cexpr
   rescue Exception => e
    $log.message(MyLogger::STDERR|MyLogger::FILE,"Error: Error during parse of user supplied expression...")
    $log.message(MyLogger::STDERR|MyLogger::FILE,"Error: #{e.message}")
    $log.message(MyLogger::FILE,"#{e.backtrace}")
    abort("Cannot continue!")
   end  

 end 

end

