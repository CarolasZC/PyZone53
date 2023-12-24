"""
Author: Moo Zhen Cong

Description: Export zone file for AWS Route53

Requirement:
IAM Role need to have permission of list-hosted-zones, list-resource-record-sets for Route53 attached

Social Media:
LinkedIn: linkedin.com/in/carolaszc
"""

import subprocess
import sys
import signal
import json

class ToolsCheckingFunction:
  def tool_checking():
            subprocess.run(["aws","--version"],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            subprocess.run([sys.executable,"--version"],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

class AWSFunction:
    use_aws_profile = False
    def aws_profile():
        answer=input("Configure aws credential with profile? (Yes or press Enter to skip) \n").strip()
        aws_configure_checking_result = subprocess.run(["aws","configure","list"],capture_output=True,text=True)
        if answer.lower() =="yes":
            AWSFunction.aws_profile_name=input("Please type profile name \n")
            AWSFunction.use_aws_profile=True
            if "profile                <not set>" in aws_configure_checking_result.stdout:
                print("AWS profile is not configure. Quiting program..")
                sys.exit(1)
        else:
            if "access_key                <not set>" in aws_configure_checking_result.stdout or "secret_key                <not set>" in aws_configure_checking_result.stdout:
                print("AWS credential is not configure. Quiting program..")
                sys.exit(1)

    def aws_export_zones_value():
        while True:
            try:
                num_zones = int(input("How many DNS zones need to export? \n"))
                user_inputs = [input(f"Enter DNS Zone number {i+1}: \n") for i in range(num_zones)]
                result = subprocess.check_output(["aws","route53","list-hosted-zones", "--output", "json"] + command ,text=True)
                hosted_zone_record = json.loads(result)
                all_hosted_zones = hosted_zone_record.get("HostedZones",[])
                matching_zone = []
                exported_value = ""
                for user_input in user_inputs:
                    matching_zone.append({
                        "user_input":user_input,
                        "zone":[zone for zone in all_hosted_zones if user_input in zone["Name"]]
                    })
                for zone in matching_zone:
                    zoneID = zone["zone"][0]["Id"].replace("/hostedzone/","")
                    specific_zone_json = subprocess.check_output(["aws","route53","list-resource-record-sets",
                                                                  "--hosted-zone-id",zoneID,"--output","json"] 
                                                                  + command,text=True)
                    specific_zone = json.loads(specific_zone_json)
                    filtered_records = [record for 
                    record in specific_zone["ResourceRecordSets"] if record["Type"] not in ["SOA", "NS"]]
                    for record in filtered_records:
                        if "ResourceRecords" in record: 
                            for recordvalue in record['ResourceRecords']:
                                        exported_value = exported_value + (f"\n{record['Name'].partition('.'+user_input)[0]} {record['TTL']} {record['Type']} {recordvalue['Value']}")
                        else:
                            exported_value = exported_value + (f"\n{record['Name'].partition('.'+user_input)[0]} 300 CNAME {record['AliasTarget']['DNSName']}") 
                print(f"\nDomain TTL Type Value\n{exported_value}")   
                sys.exit(0)
            except ValueError:
                continue
            else:
                break
        
def signal_handler(signal,frame):
    print(" Keyboard Interupt. Exiting.. \n")
    sys.exit(0) 

command = []
def main():
    signal.signal(signal.SIGINT,signal_handler)
    if AWSFunction.use_aws_profile:
        command.extend(["--profile",AWSFunction.aws_profile_name])
    try:
        ToolsCheckingFunction.tool_checking()
        AWSFunction.aws_profile()
        AWSFunction.aws_export_zones_value()
    except Exception as e:
        print(f"An error occurred: {e} \n")

if __name__ == "__main__":
    main()
