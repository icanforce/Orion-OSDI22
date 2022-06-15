using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace DAG_Modeler
{
    class Data_Loader
    {
        public static Dictionary<string, Stage> load_stages_no_wait_for_max_ML(string path = "Sampled_Data", bool test = false)
        {
            Dictionary<string, Stage> allStages = new Dictionary<string, Stage>();
            allStages.Add("PCA", new Stage() { Name = "PCA" });
            allStages.Add("ParamTune", new Stage() { Name = "ParamTune" });
            allStages.Add("CombineModels", new Stage() { Name = "CombineModels" });
            allStages.Add("E2E", new Stage() { Name = "E2E" });

            string[] files_in_dir = Directory.GetFiles(path);
            for (int i = 0; i < files_in_dir.Length; i++)
            {
                if (!files_in_dir[i].Contains("rsc_"))// skip non-profile files 
                    continue;

                string[] resrouces = files_in_dir[i].Replace(".txt", "").Replace(path, "").Replace("train_", "").Replace("test_", "").Split('_');

                StreamReader sreader = new StreamReader(files_in_dir[i]);
                Dictionary<string, double> E2E = new Dictionary<string, double>();
                Dictionary<string, double> pca = new Dictionary<string, double>();
                Dictionary<string, double> train = new Dictionary<string, double>();
                Dictionary<string, double> combine = new Dictionary<string, double>();

                int light_index = -1;

                while (!sreader.EndOfStream)
                {
                    light_index += 1;
                    string line = sreader.ReadLine();
                    string[] parts = line.Split(new string[] { " " }, StringSplitOptions.RemoveEmptyEntries);

                    int pca_value = 0;
                    int train_value =0;
                    int combine_value = 0;
                    int E2E_value = 0;

                    foreach (string p in parts)
                    {
                        string[] sub_parts = p.Split(':');
                        if (sub_parts[0] == "PCA")
                        {
                            pca_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "ParamTune")
                        {
                            train_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "CombineModels")
                        {
                            combine_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "E2E")
                        {
                            E2E_value = Int32.Parse(sub_parts[1]);
                        }
                    }

                    E2E.Add(light_index.ToString(), E2E_value);

                    for (int k = 0; k < 30; k++)
                    {
                        string light_chunk = k.ToString();

                        pca.Add(light_index + "_" + light_chunk, pca_value);
                        train.Add(light_index + "_" + light_chunk, train_value);
                        combine.Add(light_index + "_" + light_chunk, combine_value);

                    }
                }
                if (!test)
                {

                    if (!allStages["PCA"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[1])))
                    {
                        allStages["PCA"].Resource_to_latency_list.Add(Int32.Parse(resrouces[1]), pca.Values.ToList());
                    }

                    if (!allStages["ParamTune"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[2])))
                    {
                        allStages["ParamTune"].Resource_to_latency_list.Add(Int32.Parse(resrouces[2]), train.Values.ToList());
                        allStages["ParamTune"].Stage_Conditional_CDF.Add(long.Parse(resrouces[2]), CDF_PDF_Manager.get_conditional_cdf(train));
                    }

                    if (!allStages["CombineModels"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[3])))
                    {
                        allStages["CombineModels"].Resource_to_latency_list.Add(Int32.Parse(resrouces[3]), combine.Values.ToList());
                    }
                }
                allStages["E2E"].Resource_to_latency_list.Add(long.Parse(resrouces[1] + resrouces[2] + resrouces[3]), E2E.Values.ToList());
            }

            foreach (Stage s in allStages.Values)
            {
                s.fill_PDF_CDF();
                s.extractMeanStd();
            }
            return allStages;
        }
        public static Dictionary<string, Stage> load_stages_no_wait_for_max_Video(string path = "Sampled_Data", bool test = false, bool add_layer = false, bool add_synthetic_classify = false, int synthetic_classify = 0)
        {
            Dictionary<string, Stage> allStages = new Dictionary<string, Stage>();
            allStages.Add("Split", new Stage() { Name = "Split" });
            allStages.Add("Extract", new Stage() { Name = "Extract" });
            //if (add_layer)
            //    allStages.Add("shuffle", new Stage() { Name = "shuffle" });
            allStages.Add("Classify", new Stage() { Name = "Classify" });
            allStages.Add("Extract_Classify_Frame", new Stage() { Name = "Extract_Classify_Frame" });
            allStages.Add("Split_Extract_Classify_Frame", new Stage() { Name = "Split_Extract_Classify_Frame" });
            allStages.Add("E2E", new Stage() { Name = "E2E" });

            string[] files_in_dir = Directory.GetFiles(path);
            for (int i = 0; i < files_in_dir.Length; i++)
            {
                if (!files_in_dir[i].Contains("rsc_"))
                    continue;

                string[] resrouces = files_in_dir[i].Replace(".txt", "").Replace(path, "").Split('_');

                StreamReader sreader = new StreamReader(files_in_dir[i]);
                Dictionary<string, double> E2E = new Dictionary<string, double>();
                Dictionary<string, double> split = new Dictionary<string, double>();
                Dictionary<string, double> extract = new Dictionary<string, double>();
                Dictionary<string, double> classify = new Dictionary<string, double>();

                Dictionary<string, double> extract_classify = new Dictionary<string, double>();
                Dictionary<string, double> split_extract_classify = new Dictionary<string, double>();

                int video_index = -1;

                while (!sreader.EndOfStream)
                {
                    video_index += 1;
                    string line = sreader.ReadLine();
                  
                    int split_value = 0;
                    int extract_value = 0;
                    int classify_value = 0;
                    int E2E_value = 0;
                    string[] parts = line.Split(new string[] { " " }, StringSplitOptions.RemoveEmptyEntries);

                    foreach (string p in parts)
                    {
                        string[] sub_parts = p.Split(':');
                        if(sub_parts[0] == "Split")
                        {
                            split_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "Extract")
                        {
                            extract_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "Classify")
                        {
                            classify_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "E2E")
                        {
                            E2E_value = Int32.Parse(sub_parts[1]);
                        }
                    }


                    E2E.Add(video_index.ToString(), E2E_value);
                    for (int k = 0; k < 30; k++)
                    {
                        string video_chunk = k.ToString();

                        split.Add(video_index + "_" + video_chunk, split_value);
                        extract.Add(video_index + "_" + video_chunk, extract_value);
                        classify.Add(video_index + "_" + video_chunk, classify_value);
                        extract_classify.Add(video_index + "_" + video_chunk, (extract_value + classify_value));
                        split_extract_classify.Add(video_index + "_" + video_chunk, (split_value + extract_value + classify_value));
                    }
                }
                if (!test)
                {
                    double[] classify_values = classify.Values.ToArray();
                    //double split_interworker_nmi = get_NMI_between_workers(split, "split");
                    //double extract_interworker_nmi = get_NMI_between_workers(extract, "extract");
                    //double classify_interworker_nmi = get_NMI_between_workers(classify, "calssify");

                    //double extract_classify_interworker_correl = get_correlation_between_workers(extract_classify);
                   
                    if (!allStages["Split"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[1])))
                    {
                        allStages["Split"].Resource_to_latency_list.Add(Int32.Parse(resrouces[1]), split.Values.ToList());
                    }

                    if (!allStages["Extract"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[2])))
                    {
                        allStages["Extract"].Resource_to_latency_list.Add(Int32.Parse(resrouces[2]), extract.Values.ToList());
                        allStages["Extract"].Stage_Conditional_CDF.Add(long.Parse(resrouces[2]), CDF_PDF_Manager.get_conditional_cdf(extract));
                    }

                    if (!allStages["Classify"].Resource_to_latency_list.ContainsKey(Int32.Parse(resrouces[3])))
                    {
                        List<double> combined_sharpen_classify = classify.Values.ToList();
                     
                        allStages["Classify"].Resource_to_latency_list.Add(Int32.Parse(resrouces[3]), combined_sharpen_classify);
                        allStages["Classify"].Stage_Conditional_CDF.Add(long.Parse(resrouces[3]), CDF_PDF_Manager.get_conditional_cdf(classify));
                    }

                    if (!allStages["Extract_Classify_Frame"].Resource_to_latency_list.ContainsKey(Int32.Parse((resrouces[2] + resrouces[3]))))
                    {
                        allStages["Extract_Classify_Frame"].Resource_to_latency_list.Add(long.Parse(resrouces[2] + resrouces[3]), extract_classify.Values.ToList());
                        allStages["Extract_Classify_Frame"].Stage_Conditional_CDF.Add(long.Parse(resrouces[2] + resrouces[3]), CDF_PDF_Manager.get_conditional_cdf(extract_classify));
                    }
                    if (!allStages["Split_Extract_Classify_Frame"].Resource_to_latency_list.ContainsKey(long.Parse((resrouces[1] + resrouces[2] + resrouces[3]))))
                    {
                        allStages["Split_Extract_Classify_Frame"].Resource_to_latency_list.Add(long.Parse(resrouces[1] + resrouces[2] + resrouces[3]), extract_classify.Values.ToList());
                        allStages["Split_Extract_Classify_Frame"].Stage_Conditional_CDF.Add(long.Parse(resrouces[1] + resrouces[2] + resrouces[3]), CDF_PDF_Manager.get_conditional_cdf(split_extract_classify));
                    }
                }
                allStages["E2E"].Resource_to_latency_list.Add(long.Parse(resrouces[1] + resrouces[2] + resrouces[3]), E2E.Values.ToList());
            }
           
            foreach (Stage s in allStages.Values)
            {
                s.fill_PDF_CDF();
                s.extractMeanStd();
            }
            return allStages;
        }

        public static Dictionary<string, Stage> load_stages_no_wait_for_max_Chatbot(string path, bool test = false, bool add_layer = false)
        {
            Dictionary<string, Stage> allStages = new Dictionary<string, Stage>();

            allStages.Add("SplitChatBot", new Stage() { Name = "SplitChatBot" });
            allStages.Add("TrainIntentClassifier", new Stage() { Name = "TrainIntentClassifier" });
            allStages.Add("E2E", new Stage() { Name = "E2E" });
            string[] dirs_in_dir = Directory.GetFiles(path);

            for (int i = 0; i < dirs_in_dir.Length; i++)
            {
                string[] resources = dirs_in_dir[i].Split('_');
                StreamReader sreader = new StreamReader(dirs_in_dir[i]);
                List<double> split_ChatBot = new List<double>();
                List<double> train_classifier = new List<double>();
                List<double> e2e = new List<double>();
                while (!sreader.EndOfStream)
                {
                    string line = sreader.ReadLine();
                    int split_value = 0;
                    int train_value = 0;
                    int E2E_value = 0;
                    string[] parts = line.Split(new string[] { " " }, StringSplitOptions.RemoveEmptyEntries);

                    foreach (string p in parts)
                    {
                        string[] sub_parts = p.Split(':');
                        if (sub_parts[0] == "SplitChatBot")
                        {
                            split_value = Int32.Parse(sub_parts[1]);
                        }
                        else if (sub_parts[0] == "TrainIntentClassifier")
                        {
                            train_value = Int32.Parse(sub_parts[1]);
                        }
                       
                        else if (sub_parts[0] == "E2E")
                        {
                            E2E_value = Int32.Parse(sub_parts[1]);
                        }
                    }
                    split_ChatBot.Add(split_value);
                    train_classifier.Add(train_value);
                    e2e.Add(E2E_value);
                }
                allStages["SplitChatBot"].Resource_to_latency_list.Add(Int32.Parse(resources[2]), split_ChatBot);
                allStages["TrainIntentClassifier"].Resource_to_latency_list.Add(Int32.Parse(resources[2]), train_classifier);
                allStages["E2E"].Resource_to_latency_list.Add(Int32.Parse(resources[2]), e2e);

            }
            foreach (Stage s in allStages.Values)
            {
                s.fill_PDF_CDF();
                s.extractMeanStd();
            }
            return allStages;
        }
    }
}
