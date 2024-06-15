package main

import (
	"fmt"
	"sync"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/kinesis"
	"github.com/google/uuid"
)

func main() {
	// Initialize AWS session and Kinesis client
	sess := session.Must(session.NewSession(&aws.Config{
		Region: aws.String("us-east-1"), // Set your desired region
	}))
	kinesisClient := kinesis.New(sess)
	kinesisStreamName := aws.String("adapted_kinesis")

	// Your records (up to 500 records per request)

	records_500 := make([]*kinesis.PutRecordsRequestEntry, 500)
	for i := 0; i < 500; i++ {
		records_500[i] = &kinesis.PutRecordsRequestEntry{
			Data:         []byte("data"),
			PartitionKey: aws.String(uuid.New().String()),
		}
	}

	// result, err := kinesisClient.PutRecords(&kinesis.PutRecordsInput{
	// 	Records:    records_500,
	// 	StreamName: aws.String("adapted_kinesis"),
	// })
	// if err != nil {
	// 	fmt.Println("Error sending record:", err)
	// }

	// Send records in parallel
	syncGroupCount := 20

	var wg sync.WaitGroup
	for range syncGroupCount {
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
				fmt.Println("Failed records:", *result.FailedRecordCount)
			} else {
				fmt.Println("Records sent successfully")
			}
		}(records_500)
	}
	wg.Wait()


}
