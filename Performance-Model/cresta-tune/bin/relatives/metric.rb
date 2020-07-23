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

# Metric class, support loading and comparing metrics

class Metric
 DEFAULT_REGEXP=/([-+]?\d*\.?\d+([eEdD][-+]?\d+)?)\D*$/

 # take last number found in string
 def Metric.fromString(string,pattern)

  if (pattern.nil?) 
     regexp=DEFAULT_REGEXP
    else
     regexp = pattern
    end

    match=""
    string.each_line { |s|
      s.scan(regexp){
       match = $1
       }
    }

   if (match.nil?)
     return nil
    else
     # Map any fortran d/D floating-point numbers
      return match.sub(/[dD]/,"e")
    end

  end

  # Returns true if a is better than b under operation op
  def Metric.cmp(a,b,op)

   if (op == "min")
     return a.to_f < b.to_f
    elsif (op == "max" )
     return a.to_f > b.to_f
    end

  end

  def Metric.op(a,b,op)
   if op == "/"
    return a.to_f / b.to_f
   end
  end

  # Aggregate the metrics from the repeat runs
  def Metric.aggregate(metrics,op)

   if (op == "average")
     sum = 0
     metrics.each { |m| sum+=m }
     return sum / metrics.size
    else
     result = metrics[0]
     metrics.each { |m| result = m if Metric.cmp(m,result,op) }
     return result
    end

  end

  # Get metric from last number in the file 
  def Metric.fromFile(fname,pattern)

   if (pattern.nil?) 
      regexp=DEFAULT_REGEXP
    else
     regexp = pattern
    end

    begin
    mfile = File.open(fname)
    rescue Exception => e
      $log.message(MyLogger::STDERR|MyLogger::FILE,"Error during open of metric file: #{e.message}")
      abort("Cannot continue")
    end
    while line = mfile.gets

      match=regexp.match(line)
      if (!match.nil?)
       metric=match[1].sub(/[dD]/,"e")
      end

    end

   mfile.close()
   return metric

  end

end

