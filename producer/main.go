package main

import (
	"fmt"
	// "log"
	// "strconv"
	"sync"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/kinesis"
	"github.com/google/uuid"
	// "github.com/spf13/viper"
)

type ExperimentSetup struct {
    burstSize int
    msLag int
}

func main() {
	// Initialize AWS session and Kinesis client
	sess := session.Must(session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"), // Set your desired region
	}))
	kinesisClient := kinesis.New(sess)
	kinesisStreamName := aws.String("adapted_kinesis")

	recordSize := 250

	records := make([]*kinesis.PutRecordsRequestEntry, recordSize)
	for i := 0; i < recordSize; i++ {
		records[i] = &kinesis.PutRecordsRequestEntry{
			Data:         []byte("data"),
			PartitionKey: aws.String(uuid.New().String()),
		}
	}

    experimentRanges := [4]ExperimentSetup{
        {burstSize: 2, msLag: 500},
        {burstSize: 8, msLag: 100},
        {burstSize: 2, msLag: 300},
        {burstSize: 6, msLag: 100},
    }

    start_time := time.Now()

    currentExperiment := 0

	for {
		// viper.SetConfigFile(".env")


		// err := viper.ReadInConfig()
		// if err != nil {
		// 	log.Fatalf("Error reading config file, %s", err)
		// }

		// burstEnv, ok := viper.Get("BURST").(string)

		// if !ok {
		// 	log.Fatal("Error converting BURST to int")
		// }

		// burstSize, err := strconv.Atoi(burstEnv)
		// if err != nil {
		// 	log.Fatalf("Error converting BURST to int, %s", err)
		// }

        burstSize := experimentRanges[currentExperiment].burstSize

		fmt.Println("Burst size:", burstSize)
		totalFailed := 0
		var wg sync.WaitGroup
		for range burstSize {
			wg.Add(1)
			go func(r []*kinesis.PutRecordsRequestEntry) {
				defer wg.Done()
				result, err := kinesisClient.PutRecords(&kinesis.PutRecordsInput{
					Records:    r,
					StreamName: kinesisStreamName,
				})
				if err != nil {
					fmt.Println("Error sending record:", err)
					return
				}

				if *result.FailedRecordCount != 0 {
					// fmt.Println("Failed records:", *result.FailedRecordCount)
					totalFailed += 1
				}
				// else {
				//     fmt.Println("Records sent successfully")
				// }
			}(records)
		}
		wg.Wait()
		fmt.Println("Burst sent, failed records:", totalFailed)

		// msLagEnv, ok := viper.Get("MS_LAG").(string)

		// if !ok {
		// 	log.Fatal("Error converting MS_LAG to int")
		// }

		// msLag, err := strconv.Atoi(msLagEnv)
		// if err != nil {
		// 	log.Fatalf("Error converting msLag to int, %s", err)
		// }

        msLag := experimentRanges[currentExperiment].msLag

        currentExperimentTime := time.Now()

        diff := currentExperimentTime.Sub(start_time)
        if diff.Minutes() > 5 {
            currentExperiment += 1
            start_time = currentExperimentTime

            if currentExperiment == len(experimentRanges) {
                fmt.Println("All experiments completed")
                break
            }
        }
        
		time.Sleep(time.Duration(msLag) * time.Millisecond)
	}

}
