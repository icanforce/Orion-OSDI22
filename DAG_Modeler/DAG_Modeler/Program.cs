using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DAG_Modeler
{
    class Program
    {
        static void Main(string[] args)
        {
            // Start Modeler for Video-Analytics app
            double latency_percentile = 95;
            double latency_target = 25000;

            Start_Model_Video(latency_percentile, latency_target);

            Console.WriteLine();
            Console.WriteLine();
            // Start Modeler for ML pipeline app
            latency_percentile = 95;
            latency_target = 25000;

            Start_Model_ML(latency_percentile, latency_target);

            Console.WriteLine();
            Console.WriteLine();

  
            // Start Modeler for ChatBot app
            latency_percentile = 95;
            latency_target = 25000;

            Start_Model_ChatBot(latency_percentile, latency_target);

        }

        static void Start_Model_Video(double latency_percentile, double latency_target)
        {
            Dictionary<string, Stage> all_train_stages_data = null;
            Dictionary<string, Stage> all_validate_stages_data = null;
            Dictionary<string, Stage> all_test_stages_data = null;

            
            // Load training and testing profiled data

            all_train_stages_data = Data_Loader.load_stages_no_wait_for_max_Video("Video_Analytics_Data/", false, false);
            
            // Intial state
            int split_min_memory = 1000;
            int extract_min_memory = 1000;
            int classify_min_memory = 1000;

            int assume_independence = 0;
            CDF E2E_CDF = CDF_PDF_Manager.Get_E2E_CDF_Video(assume_independence, all_train_stages_data, split_min_memory, extract_min_memory, classify_min_memory);

            double current_latency = double.MaxValue; 
            int index = -1;
            for (int i = 0; i < E2E_CDF.Percentiles.Count; i++)
            {
                if (Math.Abs(latency_percentile - E2E_CDF.Percentiles[i]) < 1)
                {
                    current_latency = E2E_CDF.Values[i];
                    index = i;
                    break;
                }
            }
            int count = 0;
            CDF best_cdf = null;
            double target = latency_target;

            while (current_latency > target)// - (latency_target*0.1))
            {
                var start = DateTime.Now;

                Console.WriteLine("Evaluating: Split= " + split_min_memory + "\t" + " Extract= " + extract_min_memory + "\t" + " Classify= " + classify_min_memory);
                int split_min_memory_step = split_min_memory;
                if (split_min_memory < 10240)
                    split_min_memory_step = split_min_memory + 64;

                int extract_min_memory_step = extract_min_memory;
                if (extract_min_memory < 10240)
                    extract_min_memory_step = extract_min_memory + 64;


                int classify_min_memory_step = classify_min_memory;
                if (classify_min_memory < 10240)
                    classify_min_memory_step = classify_min_memory + 64;

                var start1 = DateTime.Now;
                CDF E2E_CDF_Split_Step = CDF_PDF_Manager.Get_E2E_CDF_Video(assume_independence, all_train_stages_data, split_min_memory_step, extract_min_memory, classify_min_memory);
                var end1 = DateTime.Now;
                var diff1 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;
                CDF E2E_CDF_Extract_Step = CDF_PDF_Manager.Get_E2E_CDF_Video(assume_independence, all_train_stages_data, split_min_memory, extract_min_memory_step, classify_min_memory);
                end1 = DateTime.Now;
                var diff2 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;

                CDF E2E_CDF_Classify_Step = CDF_PDF_Manager.Get_E2E_CDF_Video(assume_independence, all_train_stages_data, split_min_memory, extract_min_memory, classify_min_memory_step);
                end1 = DateTime.Now;
                var diff3 = (end1 - start1).TotalMilliseconds.ToString();

                int best_cdf_index = -1;
                if ((E2E_CDF_Split_Step.Values[index] < E2E_CDF_Extract_Step.Values[index]) && (E2E_CDF_Split_Step.Values[index] < E2E_CDF_Classify_Step.Values[index]) && split_min_memory < 10240)
                {
                    best_cdf_index = 0;
                    split_min_memory = split_min_memory_step;
                    best_cdf = E2E_CDF_Split_Step;
                }
                else if ((E2E_CDF_Extract_Step.Values[index] < E2E_CDF_Split_Step.Values[index]) && (E2E_CDF_Extract_Step.Values[index] < E2E_CDF_Classify_Step.Values[index]) && extract_min_memory < 10240)
                {
                    best_cdf_index = 1;
                    extract_min_memory = extract_min_memory_step;
                    best_cdf = E2E_CDF_Extract_Step;
                }
                else if ((E2E_CDF_Classify_Step.Values[index] < E2E_CDF_Split_Step.Values[index]) && (E2E_CDF_Classify_Step.Values[index] < E2E_CDF_Extract_Step.Values[index]) && classify_min_memory < 10240)
                {
                    best_cdf_index = 2;
                    classify_min_memory = classify_min_memory_step;
                    best_cdf = E2E_CDF_Classify_Step;
                }
                else if (split_min_memory == 10240 && classify_min_memory < 10240 && extract_min_memory < 10240)
                {
                    if (E2E_CDF_Classify_Step.Values[index] < E2E_CDF_Extract_Step.Values[index])
                    {
                        best_cdf_index = 2;
                        classify_min_memory = classify_min_memory_step;
                        best_cdf = E2E_CDF_Classify_Step;
                    }
                    else
                    {
                        best_cdf_index = 1;
                        extract_min_memory = extract_min_memory_step;
                        best_cdf = E2E_CDF_Extract_Step;
                    }
                }
                else if (extract_min_memory == 10240 && classify_min_memory == 10240 && split_min_memory < 10240)
                {
                    best_cdf_index = 0;
                    split_min_memory = split_min_memory_step;
                    best_cdf = E2E_CDF_Split_Step;
                }
                current_latency = best_cdf.Values[index];
                Console.WriteLine("Percentile = " + (index+1) + " Best index = " + best_cdf_index + " with Latency= " + current_latency + " steps= " + count);
                count++;
                if (count > 10000)
                {
                    break;
                }
                var end = DateTime.Now;

                var difference = (end - start).TotalMilliseconds.ToString();
            }

            Console.WriteLine("+++++++++++++++++++++++");
            Console.WriteLine("Video Best-First-Search (BFS) completed");
            Console.WriteLine("Best VM Sizes: Split= " + split_min_memory + "mb\t" + " Extract= " + extract_min_memory + "mb\t" + " Classify= " + classify_min_memory + "mb");

            return;

        }
        
        static void Start_Model_ML(double latency_percentile, double latency_target)
        {
            Dictionary<string, Stage> all_train_stages_data = null;
            all_train_stages_data = Data_Loader.load_stages_no_wait_for_max_ML(@"ML_Pipeline_Data/");

            // Intial state
            int pca_min_memory = 1000;
            int train_min_memory = 1000;
            int combine_min_memory = 1000;

            CDF E2E_CDF = CDF_PDF_Manager.Get_E2E_CDF_ML(all_train_stages_data, pca_min_memory, train_min_memory, combine_min_memory,1);
            double current_latency = double.MaxValue;
            double current_cost = 0;
            int index = -1;
            for (int i = 0; i < E2E_CDF.Percentiles.Count; i++)
            {
                if (Math.Abs(latency_percentile - E2E_CDF.Percentiles[i]) < 1)
                {
                    current_latency = E2E_CDF.Values[i];
                    index = i;
                    break;
                }
            }
            int count = 0;
            CDF best_cdf = null;
            double best_cost = double.MaxValue;
            CDF best_cost_CDF = null;

            while (current_latency > latency_target || (current_cost - best_cost) < (0.03 * best_cost))// - (latency_target*0.1))
            {
                var start = DateTime.Now;

                Console.WriteLine("Evaluating: PCA= " + pca_min_memory + "\t" + " Train= " + train_min_memory + "\t" + " Combine= " + combine_min_memory);
                int pca_min_memory_step = pca_min_memory;
                if (pca_min_memory < 10240)
                    pca_min_memory_step = pca_min_memory + 64;

                int train_min_memory_step = train_min_memory;
                if (train_min_memory < 10240)
                    train_min_memory_step = train_min_memory + 64;


                int combine_min_memory_step = combine_min_memory;
                if (combine_min_memory < 10240)
                    combine_min_memory_step = combine_min_memory + 64;

                var start1 = DateTime.Now;
                CDF E2E_CDF_Pca_Step = CDF_PDF_Manager.Get_E2E_CDF_ML(all_train_stages_data, pca_min_memory_step, train_min_memory, combine_min_memory);
                var end1 = DateTime.Now;
                var diff1 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;
                CDF E2E_CDF_Train_Step = CDF_PDF_Manager.Get_E2E_CDF_ML(all_train_stages_data, pca_min_memory, train_min_memory_step, combine_min_memory);
                end1 = DateTime.Now;
                var diff2 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;

                CDF E2E_CDF_Combine_Step = CDF_PDF_Manager.Get_E2E_CDF_ML(all_train_stages_data, pca_min_memory, train_min_memory, combine_min_memory_step);
                end1 = DateTime.Now;
                var diff3 = (end1 - start1).TotalMilliseconds.ToString();

                int best_cdf_index = -1;
                if ((E2E_CDF_Pca_Step.Values[index] < E2E_CDF_Train_Step.Values[index]) && (E2E_CDF_Pca_Step.Values[index] < E2E_CDF_Combine_Step.Values[index]) && pca_min_memory < 10240)
                {
                    best_cdf_index = 0;
                    pca_min_memory = pca_min_memory_step;
                    best_cdf = E2E_CDF_Pca_Step;
                }
                else if ((E2E_CDF_Train_Step.Values[index] < E2E_CDF_Pca_Step.Values[index]) && (E2E_CDF_Train_Step.Values[index] < E2E_CDF_Combine_Step.Values[index]) && train_min_memory < 10240)
                {
                    best_cdf_index = 1;
                    train_min_memory = train_min_memory_step;
                    best_cdf = E2E_CDF_Train_Step;
                }
                else if ((E2E_CDF_Combine_Step.Values[index] < E2E_CDF_Pca_Step.Values[index]) && (E2E_CDF_Combine_Step.Values[index] < E2E_CDF_Train_Step.Values[index]) && combine_min_memory < 10240)
                {
                    best_cdf_index = 2;
                    combine_min_memory = combine_min_memory_step;
                    best_cdf = E2E_CDF_Combine_Step;
                }
                else if (train_min_memory == 10240 && combine_min_memory < 10240 && pca_min_memory < 10240)
                {
                    if (E2E_CDF_Combine_Step.Values[index] < E2E_CDF_Pca_Step.Values[index])
                    {
                        best_cdf_index = 2;
                        combine_min_memory = combine_min_memory_step;
                        best_cdf = E2E_CDF_Combine_Step;
                    }
                    else
                    {
                        best_cdf_index = 0;
                        pca_min_memory = pca_min_memory_step;
                        best_cdf = E2E_CDF_Pca_Step;
                    }
                }
                else if (train_min_memory == 10240 && combine_min_memory == 10240 && pca_min_memory < 10240)
                {
                    best_cdf_index = 0;
                    pca_min_memory = pca_min_memory_step;
                    best_cdf = E2E_CDF_Pca_Step;
                }
                current_latency = best_cdf.Values[index];
                if (current_latency < latency_target)
                {
                    if (current_cost < best_cost)
                    {
                        best_cost = current_cost;
                        best_cost_CDF = best_cdf;
                    }
                }
                Console.WriteLine("Percentile = " + index + " Best index = " + best_cdf_index + " with Latency= " + current_latency + " steps= " + count);
                count++;
                if (count > 10000)
                {
                    break;
                }
                var end = DateTime.Now;

                var difference = (end - start).TotalMilliseconds.ToString();
            }

            Console.WriteLine("+++++++++++++++++++++++");
            Console.WriteLine("ML Best-First-Search (BFS) completed");
            Console.WriteLine("Best VM Sizes: PCA= " + pca_min_memory + "mb\t" + " Train= " + train_min_memory + "mb\t" + " Combine= " + combine_min_memory + "mb");


            return;
        }

        static void Start_Model_ChatBot(double latency_percentile, double latency_target)
        {
            Dictionary<string, Stage> all_train_stages_data = null;
            Dictionary<string, Stage> all_test_stages_data = null;
            all_train_stages_data = Data_Loader.load_stages_no_wait_for_max_Chatbot(@"ChatBot_Data/", false, true);
        
            int Split_chat_source = 1024;
            int Train_chat_source = 1024;

            CDF E2E_CDF = CDF_PDF_Manager.Get_E2E_CDF_Chat(1, all_train_stages_data, all_test_stages_data, Split_chat_source, Train_chat_source);
            double current_latency = double.MaxValue;
            int index = -1;
            for (int i = 0; i < E2E_CDF.Percentiles.Count; i++)
            {
                if (Math.Abs(latency_percentile - E2E_CDF.Percentiles[i]) < 1)
                {
                    current_latency = E2E_CDF.Values[i];
                    index = i;
                    break;
                }
            }
            int count = 0;
            CDF best_cdf = null;

            while (current_latency > (0.7*latency_target))// - (latency_target*0.1))
            {
                var start = DateTime.Now;

                Console.WriteLine("Evaluating: Split= " + Split_chat_source + "\t" + " Train= " + Train_chat_source);
                int Split_chat_source_step = Split_chat_source;
                if (Split_chat_source < 10240)
                    Split_chat_source_step = Split_chat_source + 64;

                int Train_chat_source_step = Train_chat_source;
                if (Train_chat_source < 10240)
                    Train_chat_source_step = Train_chat_source + 64;

                var start1 = DateTime.Now;
                CDF E2E_CDF_Split_Step = CDF_PDF_Manager.Get_E2E_CDF_Chat(1, all_train_stages_data, all_test_stages_data, Split_chat_source_step, Train_chat_source);
                var end1 = DateTime.Now;
                var diff1 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;
                CDF E2E_CDF_Train_Step = CDF_PDF_Manager.Get_E2E_CDF_Chat(1, all_train_stages_data, all_test_stages_data, Split_chat_source, Train_chat_source_step);
                end1 = DateTime.Now;
                var diff2 = (end1 - start1).TotalMilliseconds.ToString();

                start1 = DateTime.Now;

                int best_cdf_index = -1;
                if ((E2E_CDF_Split_Step.Values[index] < E2E_CDF_Train_Step.Values[index]) && Split_chat_source < 10240)
                {
                    best_cdf_index = 0;
                    Split_chat_source = Split_chat_source_step;
                    best_cdf = E2E_CDF_Split_Step;
                }
                else if (Train_chat_source == 10240)
                {
                    best_cdf_index = 0;
                    Split_chat_source = Split_chat_source_step;
                    best_cdf = E2E_CDF_Split_Step;
                }
                else
                {
                    best_cdf_index = 1;
                    Train_chat_source = Train_chat_source_step;
                    best_cdf = E2E_CDF_Train_Step;
                }
                current_latency = best_cdf.Values[index];
                Console.WriteLine("Percentile = " + index + " Best index = " + best_cdf_index + " with Latency= " + current_latency + " steps= " + count);
                count++;
                if (count > 10000)
                {
                    break;
                }
                var end = DateTime.Now;

                var difference = (end - start).TotalMilliseconds.ToString();
            }
            Console.WriteLine("+++++++++++++++++++++++");
            Console.WriteLine("ChatBot Best-First-Search (BFS) completed");
            Console.WriteLine("Best VM Sizes: Split= " + Split_chat_source + "mb\t" + " Train= " + Train_chat_source+ "mb");

            return;
        }

    }
}
