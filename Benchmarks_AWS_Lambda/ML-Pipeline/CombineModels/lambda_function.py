import json

def lambda_handler(event, context):
    if("dummy" in event):
        return {'dummy':'dummy combine, doing nothing'}
        
    configs_list = []
    accuracy_list = []
    for i in range(len(event)):
        for j in range(len(event[i]["trees_max_depthes"])):
            configs_list.append(event[i]["trees_max_depthes"][j])
            accuracy_list.append(event[i]["accuracies"][j])
        
    Z = [x for _, x in sorted(zip(accuracy_list, configs_list))] 
    returned_configs = Z[-10:len(accuracy_list)]
    returned_latecy = sorted(accuracy_list)[-10:len(accuracy_list)]
    print(returned_configs)
    print(returned_latecy)
    # TODO implement
    return {
        'statusCode': 200,
        'accuracy': returned_configs,
        'returned_latecy': returned_latecy,
        'all_data': json.dumps(str(event)),
        'body': json.dumps('Hello from Lambda!')
    }

