# Overview

This repository contains public releases of Microsoft Azure traces for the benefit of the research and academic community.
There is currently one classes of data available: 

* Aggreggated Data: sample data aggregated by DAG's characteristics (e.g., width, depth), collected over two week in 2021.

## Agreggated Data 

### DAG Structure
Data sample of the structure (width and depth) of DAGs. The data is aggregated either by *width*, *depth* or *total number of nodes* in the DAG. The data was collected from 10/18/2021 to 10/31/2021.
<br/>**File:** dag_structure.xls 

### Intermediate data
Data sample of the intermediate data size passed accross the entire DAG. The data is aggregated by *data size passed (in bytes)*. The data was collected from 10/18/2021 to 10/31/2021.
<br/>**File:** dag_intermediate-date.xls 

 | Tab | Description |
 | --- |  --- |
 | all dags    | Data passed (in bytes) for all DAGs. |
 | fan-out 32  | Data passed (in bytes) for DAGs with a maximum fan-out >= 32. |
 | fan-out 128 | Data passed (in bytes) for DAGs with a maximum fan-out >= 128. |

### Corelation between E2E latency, Max Skew, and Intermediate Data Size
Data sample for DAG latency per max skew and intermediate data size passed on a DAG. The data is aggregated by *E2E latency in milliseconds*. The data was collected from 10/18/2021 to 10/31/2021.
<br/>**File:** dag_correlation.xls 
 
 | Tab | Description |
 | --- |  --- |
 | data <1M  | E2E latency for DAGs with intermediate data size less than 1M. |
 | data 1M+  | E2E latency for DAGs with intermediate data size higher than 1M. |
 | skew <100 | E2E latency for DAGs with a maximum skew less than 100. |
 | skew 100+ | E2E latency for DAGs with a maximum skew higher than 100. |
