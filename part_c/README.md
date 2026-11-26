# Part C — Performance Testing

This folder contains the dynamic performance test suite for the Todo Manager REST API.

## Scope

The suite measures three operations on Todo objects:

- **CREATE:** POST `/todos`
- **UPDATE:** POST `/todos/{id}` (the update method used by the existing Part A/Part B tests)
- **DELETE:** DELETE `/todos/{id}`

Each object is populated with randomly generated title and description data. The default workload sizes are 100, 500, 1,000, and 2,000 objects. Each workload is repeated three times.

## Prerequisites

1. Python 3.10+
2. Dependencies from the repository root:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Start the Todo Manager API in a separate terminal:
   ```powershell
   java -jar runTodoManagerRestAPI-1.5.5.jar
   ```

The default API URL is `http://localhost:4567`. Set `TODO_API_URL` is not currently required; use `--base-url` to override the URL.

## Run

From the repository root:

```powershell
python -m part_c.performance_test
```

Customize the experiment:

```powershell
python -m part_c.performance_test --sizes 100,500,1000,2000 --repeats 3
python -m part_c.performance_test --operations create
python -m part_c.performance_test --operations update,delete --sizes 100,500
python -m part_c.performance_test --base-url http://localhost:4567 --output part_c/results/run1.csv
```

## Measurement method

- Random payload generation is performed before timing.
- CREATE timing includes the sequence of API create requests only.
- UPDATE and DELETE objects are created before the timed section.
- UPDATE timing includes the sequence of update requests only.
- DELETE timing includes the sequence of delete requests only.
- Setup and cleanup requests are excluded from transaction timing.
- Each experiment records total elapsed time, average time per requested object, throughput, successful operations, failed operations, and cleanup errors.
- A unique run ID and UTC timestamp are recorded for traceability.

The script writes CSV results to `part_c/results/performance_results.csv` by default.

## CPU and memory monitoring

CPU utilization and available memory must be collected separately while each experiment runs. The teammate responsible for resource monitoring should record the timestamp, operation, workload size, CPU percentage, and available memory in MB, then correlate these samples with the run IDs/timestamps in the performance CSV.

On Windows, Performance Monitor can collect Processor\% Processor Time and Memory\Available MBytes. Record the sampling interval and machine configuration in the report.

## Experimental cautions

- Run the API and test runner on the same machine for consistent comparisons.
- Close unrelated high-load applications.
- Use the same API process, machine, Java version, and workload sizes for each repetition.
- Check that all operations succeeded and cleanup errors are zero before interpreting a result.
- Large workloads can take time and consume memory. Increase the workload gradually.
- The suite creates and deletes test data. Run it against the course test instance, not a shared production service.
