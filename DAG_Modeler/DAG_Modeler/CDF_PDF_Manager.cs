using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DAG_Modeler
{
    class CDF_PDF_Manager
    {
        private static CDF Get_Conditional_CDF_with_Interpolation(Dictionary<string, Stage> all_train_stages_data, string stage_name, int classify_source)
        {
            long classify_extract_joint_key = long.Parse(classify_source.ToString() + classify_source.ToString());

            if (classify_source == 576)
                classify_extract_joint_key = long.Parse("192" + classify_source.ToString());


            if (all_train_stages_data[stage_name].Stage_Conditional_CDF.ContainsKey(classify_extract_joint_key))
            {
                return all_train_stages_data[stage_name].Stage_Conditional_CDF[classify_extract_joint_key];
            }
            else
            {
                List<long> profiled_resources = all_train_stages_data[stage_name].Stage_Conditional_CDF.Keys.ToList().OrderBy(x => x).ToList();
                for (int i = 0; i < profiled_resources.Count - 1; i++)
                {
                    if (classify_extract_joint_key > profiled_resources[i] && classify_extract_joint_key < profiled_resources[i + 1])
                    {
                        PDF pdf1 = all_train_stages_data[stage_name].Stage_PDF[profiled_resources[i]];
                        PDF pdf2 = all_train_stages_data[stage_name].Stage_PDF[profiled_resources[i + 1]];


                        CDF cdf1 = CDF_PDF_Manager.get_cdf(pdf1);
                        CDF cdf2 = CDF_PDF_Manager.get_cdf(pdf2);

                        double classify_extract_joint_key_classify = Double.Parse(classify_extract_joint_key.ToString().Substring(classify_extract_joint_key.ToString().Length / 2, classify_extract_joint_key.ToString().Length / 2));
                        double cdf1_classify = Double.Parse(profiled_resources[i].ToString().Substring(profiled_resources[i].ToString().Length / 2, profiled_resources[i].ToString().Length / 2));
                        double cdf2_classify = Double.Parse(profiled_resources[i + 1].ToString().Substring(profiled_resources[i + 1].ToString().Length / 2, profiled_resources[i + 1].ToString().Length / 2));

                        double weight1 = Math.Round(((double)(classify_extract_joint_key_classify - cdf1_classify)) / (cdf2_classify - cdf1_classify), 2);
                        double weight2 = 1 - weight1;

                        CDF interpolation = CDF_PDF_Manager.get_interpolation_CDF(cdf1, cdf2, weight1, weight2);
                        return interpolation;
                    }
                }
            }
            return null;
        }

        public static CDF Get_E2E_CDF_Video(int assume_independence, Dictionary<string, Stage> all_train_stages_data, int Split_source, int Extract_source, int Classify_source, int stage_depth = 3, bool add_synthetic_stages = false)
        {
            PDF Split_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "Split", Split_source);
            PDF Extract_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "Extract", Extract_source);
            PDF Classify_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "Classify", Classify_source);

            //printCDFs(Split_PDF, Split_source, Extract_PDF, Extract_source, Classify_PDF, Classify_source, all_test_stages_data);

            PDF extract_classify_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(Extract_PDF, Classify_PDF);
            if (add_synthetic_stages)
            {
                for (int i = 3; i < stage_depth; i++)
                {
                    extract_classify_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(extract_classify_PDF, Classify_PDF);
                }
            }
            CDF extract_classify_CDF = CDF_PDF_Manager.get_cdf(extract_classify_PDF);

            CDF interpolation = Get_Conditional_CDF_with_Interpolation(all_train_stages_data, "Extract_Classify_Frame", Classify_source);

            CDF Max_joint_CDF = CDF_PDF_Manager.get_max_joint_CDF(extract_classify_CDF, 1, interpolation);

            PDF Max_PDF = null;
            if (assume_independence == 1)
            {
                CDF extract_Classify_independent_CDF = CDF_PDF_Manager.get_cdf(extract_classify_PDF);
                CDF independent_CDF = CDF_PDF_Manager.get_max_CDF(extract_Classify_independent_CDF, 6);
                Max_PDF = CDF_PDF_Manager.get_pdf(independent_CDF);
            }
            else
            {
                Max_PDF = CDF_PDF_Manager.get_pdf(Max_joint_CDF);
            }

            PDF E2E_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(Split_PDF, Max_PDF);
            for (int i = 3; i < stage_depth; i++)
            {
                E2E_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(Split_PDF, Max_PDF);
            }
            CDF E2E_CDF = CDF_PDF_Manager.get_cdf(E2E_PDF);
            return E2E_CDF;
        }

        public static CDF Get_E2E_CDF_ML(Dictionary<string, Stage> all_train_stages_data, int pca_source, int train_source, int combine_source, int N_parallel = 10)
        {
            PDF PCA_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "PCA", pca_source);
            PDF Train_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "ParamTune", train_source);
            PDF Combine_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "CombineModels", combine_source);

            //printCDFs_ML(PCA_PDF, pca_source, Train_PDF, train_source, Combine_PDF, combine_source, all_test_stages_data);


            CDF train_single_CDF = CDF_PDF_Manager.get_cdf(Train_PDF);
            CDF train_max_independent_CDF = CDF_PDF_Manager.get_max_CDF(train_single_CDF, N_parallel);

            PDF train_max_independent_PDF = CDF_PDF_Manager.get_pdf(train_max_independent_CDF);

            PDF pca_train_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(PCA_PDF, train_max_independent_PDF);
            PDF E2E_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(pca_train_PDF, Combine_PDF);

            CDF E2E_CDF = CDF_PDF_Manager.get_cdf(E2E_PDF);
            return E2E_CDF;
        }

        public static CDF Get_E2E_CDF_Chat(int assume_independence, Dictionary<string, Stage> all_train_stages_data, Dictionary<string, Stage> all_test_stages_data, int Split_chat_source, int Train_chat_source)
        {
            PDF Split_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "SplitChatBot", Split_chat_source);
            PDF Train_PDF = Get_Component_PDF_with_Interpolation(all_train_stages_data, "TrainIntentClassifier", Train_chat_source);

            CDF train_single_CDF = CDF_PDF_Manager.get_cdf(Train_PDF);
            CDF train_max_independent_CDF = CDF_PDF_Manager.get_max_CDF(train_single_CDF, 22);


            PDF train_max_independent_PDF = CDF_PDF_Manager.get_pdf(train_max_independent_CDF);

            PDF split_train_PDF = CDF_PDF_Manager.get_convolution_2_PDFs(Split_PDF, train_max_independent_PDF);

            CDF E2E_CDF = CDF_PDF_Manager.get_cdf(split_train_PDF);
            return E2E_CDF;
        }

        public static int get_nearest_index(CDF input, double percentile)
        {
            double min_diff = double.MaxValue;
            int best_index = -1;
            for (int i = 0; i < input.Percentiles.Count; i++)
            {
                double diff = Math.Abs(percentile - input.Percentiles[i]);
                if (diff < min_diff)
                {
                    min_diff = diff;
                    best_index = i;
                }
            }
            return best_index;
        }

        public static CDF get_interpolation_CDF(CDF cdf1, CDF cdf2, double cdf1_weight, double cdf2_weight)
        {
            CDF returned_CDF = new CDF();

            for (int i = 0; i < 100; i++)
            {
                returned_CDF.Percentiles.Add(i);
                int nearest_index_cdf1 = get_nearest_index(cdf1, i);
                int nearest_index_cdf2 = get_nearest_index(cdf2, i);

                //double weighted_average = cdf1.Values[nearest_index_cdf1] * cdf1_weight +
                //                          cdf2.Values[nearest_index_cdf2] * cdf2_weight;

                double weighted_average = cdf2.Values[nearest_index_cdf2] + (cdf2_weight * (cdf1.Values[nearest_index_cdf1] - cdf2.Values[nearest_index_cdf2]));

                returned_CDF.Values.Add(weighted_average);
            }

            return returned_CDF;
        }

        public static List<double> get_interpolation_LatencyLists(List<double> list1_low, List<double> list2_high, double cdf1_weight, double cdf2_weight)
        {
            List<double> returned_list = new List<double>();
            list1_low = list1_low.OrderBy(x => x).ToList();
            list2_high = list2_high.OrderBy(x => x).ToList();

            for (int i = 0; i < Math.Min(list1_low.Count, list2_high.Count); i++)
            {
                // cdf2.Values[nearest_index_cdf2] * cdf2_weight;

                double weighted_average = list2_high[i] + (cdf2_weight * (list1_low[i] - list2_high[i]));

                returned_list.Add(weighted_average);
            }
            return returned_list;
        }
        public static CDF get_cdf(PDF input_pdf)
        {
            // always round the sum of probabilities to 1
            input_pdf.Percentages[0] += 1 - input_pdf.Percentages.Sum();

            CDF returned_CDF = new CDF();
            double percentile = 0;
            while (percentile <= 100)
            {
                percentile += 1;
                returned_CDF.Percentiles.Add(percentile);
                double sum_probabilties = 0;
                for (int i = 0; i < input_pdf.Values.Count; i++)
                {
                    sum_probabilties += input_pdf.Percentages[i];
                    if ((sum_probabilties * 100) >= (percentile - 0.0000000001))
                    {
                        returned_CDF.Values.Add(input_pdf.Values[i]);
                        break;
                    }
                }
            }

            return returned_CDF;
        }

        public static CDF get_CDF_by_Division(CDF input, double ratio)
        {
            CDF returnedCDF = new CDF();
            returnedCDF.Percentiles = input.Percentiles;
            for (int i = 0; i < input.Values.Count; i++)
            {
                returnedCDF.Values.Add(ratio * input.Values[i]);
            }
            return returnedCDF;
        }
        public static PDF get_convolution_2_PDFs(PDF compPDF_1, PDF compPDF_2)
        {
            PDF returned_PDF = new PDF();

            double min_latency = compPDF_1.Values[0] + compPDF_2.Values[0]; // index 0 is min latency (assuming sorted)
            double max_latency = compPDF_1.Values[compPDF_1.Values.Count - 1] + compPDF_2.Values[compPDF_2.Values.Count - 1];

            double start = min_latency;
            while (start <= max_latency)
            {
                start += 100;
                returned_PDF.Values.Add(start);
                returned_PDF.Percentages.Add(0);
            }
            returned_PDF.Values.Add(max_latency);
            returned_PDF.Percentages.Add(0);


            for (int i = 0; i < compPDF_1.Values.Count; i++)
            {
                for (int j = 0; j < compPDF_2.Values.Count; j++)
                {
                    double sum_latency = compPDF_1.Values[i] + compPDF_2.Values[j];
                    double probability = compPDF_1.Percentages[i] * compPDF_2.Percentages[j];

                    int index = Convert.ToInt32(Math.Floor((sum_latency - min_latency) / 100));
                    if (index < returned_PDF.Percentages.Count)
                    {
                        returned_PDF.Percentages[index] += probability;
                    }
                }
            }

            return returned_PDF;
        }

        public static CDF get_max_joint_CDF_not_finished(CDF input_CDF, int N, CDF joint_CDF)
        {
            CDF returned_CDF = new CDF();
            //returned_CDF.Percentiles = input_CDF.Percentiles;
            double last_latency = 0;
            double min_latency = input_CDF.Values[0];
            double max_latency = input_CDF.Values[input_CDF.Values.Count - 1];
            double step = 100;
            double Y = min_latency;
            int percentile = 1;
            for (int i = 0; i < 101; i++)
            {
                while (Y <= max_latency)
                {
                    for (int k = 0; k < input_CDF.Percentiles.Count - 1; k++)
                    {
                        if (input_CDF.Values[k] <= Y)
                        {
                            double component_probabiltiy = input_CDF.Percentiles[k] / 100;
                            double latency = input_CDF.Values[k];
                            double min_diff = double.MaxValue;
                            int nearest_index = -1;
                            for (int v = 0; v < joint_CDF.Values.Count; v++)
                            {
                                if (Math.Abs(joint_CDF.Values[v] - latency) < min_diff)
                                {
                                    min_diff = Math.Abs(joint_CDF.Values[v] - latency);
                                    nearest_index = v;
                                }
                            }
                            double joint_probability = Math.Pow(joint_CDF.Percentiles[nearest_index] / 100, N - 1) * 100;
                            double max_probabiltiy = component_probabiltiy * joint_probability * 100;
                            if (max_probabiltiy > percentile && max_probabiltiy < (percentile + 1))
                            {
                                returned_CDF.Values.Add(Y);
                                returned_CDF.Percentiles.Add(percentile);
                                percentile += 1;
                            }
                            break;
                        }
                    }
                    Y += step;
                }
            }

            return returned_CDF;
        }
        public static CDF get_max_joint_CDF(CDF input_CDF, int N, CDF joint_CDF)
        {
            CDF returned_CDF = new CDF();
            //returned_CDF.Percentiles = input_CDF.Percentiles;
            double last_latency = 0;
            for (int i = 0; i < input_CDF.Values.Count - 1; i++)
            {
                //if (input_CDF.Percentiles[i] > 99)
                //    continue;

                double component_probabiltiy = input_CDF.Percentiles[i] / 100;
                double latency = input_CDF.Values[i];

                double min_diff = double.MaxValue;
                int nearest_index = -1;
                for (int k = 0; k < joint_CDF.Values.Count; k++)
                {
                    if (Math.Abs(joint_CDF.Values[k] - latency) < min_diff)
                    {
                        min_diff = Math.Abs(joint_CDF.Values[k] - latency);
                        nearest_index = k;
                    }
                }
                double joint_probability = Math.Pow(joint_CDF.Percentiles[nearest_index] / 100, N - 1);

                returned_CDF.Values.Add(latency);
                last_latency = latency;
                double max_probabiltiy = component_probabiltiy * joint_probability * 100;
                returned_CDF.Percentiles.Add(max_probabiltiy);
            }
            double last_max_probability = returned_CDF.Percentiles[returned_CDF.Percentiles.Count - 1];

            double component_max_latency = input_CDF.Values[input_CDF.Values.Count - 1];
            int percetnile_counter = Convert.ToInt32(last_max_probability);
            while (percetnile_counter < 100)
            {
                percetnile_counter += 1;
                double smooth_prob = (percetnile_counter - last_max_probability) / (100 - last_max_probability) * (component_max_latency - last_latency) + last_latency;

                returned_CDF.Values.Add(smooth_prob);
                returned_CDF.Percentiles.Add(percetnile_counter);
            }
            //returned_CDF.Values.Add(last_latency);
            //returned_CDF.Percentiles.Add(100);
            return returned_CDF;
        }
        public static CDF get_max_CDF(CDF input_CDF, int N)
        {
            CDF returned_CDF = new CDF();

            returned_CDF.Percentiles = input_CDF.Percentiles;
            for (int i = 0; i < returned_CDF.Percentiles.Count - 1; i++)
            {
                double max_percentile = returned_CDF.Percentiles[i];
                double component_percentile = 100 * Math.Pow(max_percentile / 100, (1.0 / N));

                int component_index = Convert.ToInt32(Math.Floor(component_percentile)) - 1;
                returned_CDF.Values.Add(input_CDF.Values[component_index]);
            }

            return returned_CDF;
        }
        public static CDF get_max_CDF_From_Latency_List(List<double> sortedLatency, double N)
        {
            CDF returnedMaxCDF = new CDF();

            for (double i = 1; i <= 100; i++)
            {
                int index = Convert.ToInt32(Math.Ceiling(Math.Pow((i / 100.0), (1.0 / N)) * (sortedLatency.Count - 1)));
                returnedMaxCDF.Percentiles.Add(i);
                returnedMaxCDF.Values.Add(sortedLatency[index]);
            }
            return returnedMaxCDF;
        }

        public static PDF get_pdf(CDF input_Cdf)
        {
            PDF returned_pdf = new PDF();
            double min_latency = input_Cdf.Values[0];

            returned_pdf.Percentages.Add((input_Cdf.Percentiles[0]) / 100 - 0);

            returned_pdf.Values.Add(min_latency);
            double prev_latency = min_latency;
            double probability = input_Cdf.Percentiles[0];
            for (int i = 1; i < input_Cdf.Values.Count; i++)
            {
                if (prev_latency < input_Cdf.Values[i])
                {
                    double added_probability = Math.Max(0, (input_Cdf.Percentiles[i] - probability) / 100);
                    returned_pdf.Percentages.Add(added_probability);
                    returned_pdf.Values.Add(prev_latency);
                    prev_latency = input_Cdf.Values[i];

                    probability = input_Cdf.Percentiles[i];
                }
            }
            returned_pdf.Percentages.Add(0.01);
            returned_pdf.Values.Add(input_Cdf.Values[input_Cdf.Values.Count - 1]);
            return returned_pdf;
        }

        public static double get_pearson_correl(double[] values1, double[] values2)
        {
            if (values1.Length != values2.Length)
                throw new ArgumentException("values must be the same length");

            var avg1 = values1.Average();
            var avg2 = values2.Average();

            var N_Sum_X_Y = values1.Length * values1.Zip(values2, (x1, y1) => x1 * y1).Sum();
            var sum_x_sum_y = values1.Sum() * values2.Sum();

            var X_pow_2 = values1.Zip(values1, (x1, y1) => x1 * y1);
            var Y_pow_2 = values2.Zip(values2, (x1, y1) => x1 * y1);

            var denom_x = values1.Length * X_pow_2.Sum() - (values1.Sum() * values1.Sum());
            var denom_y = values2.Length * Y_pow_2.Sum() - (values2.Sum() * values2.Sum());

            if (denom_x == 0 || denom_y == 0)
                return 0;

            var result = (N_Sum_X_Y - sum_x_sum_y) / Math.Sqrt(denom_x * denom_y);

            return result;
        }

        public static double compute_correlation_two_arrays(double[] values1, double[] values2)
        {
            if (values1.Length != values2.Length)
                throw new ArgumentException("values must be the same length");

            var avg1 = values1.Average();
            var avg2 = values2.Average();

            var sum1 = values1.Zip(values2, (x1, y1) => (x1 - avg1) * (y1 - avg2)).Sum();

            var sumSqr1 = values1.Sum(x => Math.Pow((x - avg1), 2.0));
            var sumSqr2 = values2.Sum(y => Math.Pow((y - avg2), 2.0));
            if (sumSqr1 == 0 || sumSqr2 == 0)
                return 0;

            var result = sum1 / Math.Sqrt(sumSqr1 * sumSqr2);

            return result;
        }

        public static PDF Get_Component_PDF_with_Interpolation(Dictionary<string, Stage> all_train_stages_data, string stage_name, int resource)
        {
            if (all_train_stages_data[stage_name].Stage_PDF.ContainsKey(resource))
            {
                return all_train_stages_data[stage_name].Stage_PDF[resource];
            }
            else
            {
                List<long> profiled_resources = all_train_stages_data[stage_name].Stage_PDF.Keys.ToList().OrderBy(x => x).ToList();
                for (int i = 0; i < profiled_resources.Count - 1; i++)
                {
                    if (resource > profiled_resources[i] && resource < profiled_resources[i + 1])
                    {
                        PDF pdf1 = all_train_stages_data[stage_name].Stage_PDF[profiled_resources[i]];
                        PDF pdf2 = all_train_stages_data[stage_name].Stage_PDF[profiled_resources[i + 1]];


                        CDF cdf1 = CDF_PDF_Manager.get_cdf(pdf1);
                        CDF cdf2 = CDF_PDF_Manager.get_cdf(pdf2);

                        double weight1 = Math.Round(((double)(resource - profiled_resources[i])) / (profiled_resources[i + 1] - profiled_resources[i]), 2);
                        double weight2 = 1 - weight1;

                        CDF interpolation = CDF_PDF_Manager.get_interpolation_CDF(cdf1, cdf2, weight1, weight2);
                        return CDF_PDF_Manager.get_pdf(interpolation);
                    }
                }
            }

            return null;
        }
        public static CDF get_conditional_cdf(Dictionary<string, double> stage)
        {
            List<string> keys = stage.Keys.ToList();

            CDF conditional_cdf = new CDF();
            Dictionary<double, double> Latency_to_probabiltiy = new Dictionary<double, double>();
            List<List<double>> all_workers_latencies = new List<List<double>>();
            for (int i = 0; i < 6; i++)
            {
                all_workers_latencies.Add(new List<double>());
            }
            double min_latency = double.MaxValue;
            double max_latency = double.MinValue;
            Dictionary<int, int> visited_keys = new Dictionary<int, int>();

            foreach (string s in keys)
            {
                int i = Int32.Parse(s.Split('_')[0]);
                if (visited_keys.ContainsKey(i))
                    continue;

                visited_keys.Add(i, i);
                for (int j = 0; j < 6; j++)
                {
                    double value = 0;
                    if (stage.ContainsKey(i + "_" + j))
                    {
                        value = stage[i + "_" + j];
                        all_workers_latencies[j].Add(stage[i + "_" + j]);
                    }
                    else
                    {
                        for (int miss = 0; miss < 6; miss++)
                        {
                            if (stage.ContainsKey(i + "_" + miss))
                            {
                                value = stage[i + "_" + miss];
                                all_workers_latencies[j].Add(stage[i + "_" + miss]);
                                break;
                            }
                        }
                    }
                    if (value < min_latency)
                    {
                        min_latency = value;
                    }
                    if (value > max_latency)
                    {
                        max_latency = value;
                    }
                }
            }

            double start = min_latency;
            double step = (max_latency - min_latency) / 100;
            bool allow_once = true;
            while (start <= max_latency)
            {
                double less_than = 0;
                double greater_than = 0;
                for (int i = 0; i < 6; i++)
                {
                    List<double> currentWorker = all_workers_latencies[i];
                    for (int j = 0; j < currentWorker.Count; j++)
                    {
                        if (currentWorker[j] <= start)
                        {
                            for (int k = 0; k < 6; k++)
                            {
                                if (all_workers_latencies[k][j] <= start)
                                {
                                    less_than++;
                                }
                                else
                                {
                                    greater_than++;
                                }
                            }
                        }
                    }
                }
                if ((less_than + greater_than) > 0)
                {
                    conditional_cdf.Values.Add(start);
                    conditional_cdf.Percentiles.Add((double)less_than / (less_than + greater_than) * 100);
                }
                start += step;
                if (allow_once == false)
                {
                    break;
                }
                if (start > max_latency)
                {
                    start = max_latency;
                    allow_once = false;
                }
            }

            return conditional_cdf;
        }

    }
}
