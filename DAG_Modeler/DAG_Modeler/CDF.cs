using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DAG_Modeler
{
    public class CDF
    {
        List<double> percentiles = new List<double>();
        List<double> values = new List<double>();

        public List<double> Percentiles { get => percentiles; set => percentiles = value; }
        public List<double> Values { get => values; set => values = value; }
    }
    public class PDF
    {
        List<double> percentages = new List<double>();
        List<double> values = new List<double>();

        public PDF()
        {

        }
        public PDF(List<double> latency_measures)
        {
            latency_measures.Sort();
            double min_latency = latency_measures.Min();
            double max_latency = latency_measures.Max();

            double start = min_latency;
            double end = min_latency + 10;
            Values.Add(end);
            double count = 0;
            int index = 0;
            while (index < latency_measures.Count)
            {
                if (latency_measures[index] >= start && latency_measures[index] <= end)
                {
                    count++;
                    index++;
                }
                else
                {
                    Percentages.Add(count / latency_measures.Count);
                    count = 0;

                    start += 10;
                    end += 10;
                    if (end > max_latency)
                    {
                        Values.Add(max_latency);
                    }
                    else
                    {
                        Values.Add(end);
                    }
                }
            }
            Percentages.Add(count / latency_measures.Count);
        }

        public List<double> Percentages { get => percentages; set => percentages = value; }
        public List<double> Values { get => values; set => values = value; }
    }

}
