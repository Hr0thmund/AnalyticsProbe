import asyncio
import configparser
import socket
from datetime import datetime
from statistics import median, mean

from icmplib import async_multiping

# The collect_metrics function takes a list of targets in dictionary form, 
# and a probe ID to include in the resutls tuple. It then resolves the
# hostnames, pings all the IPs for each hostname, takes the median result
# from each IP address, calculates the mean, tallies packet loss, and then
# wraps all this data up in a tuple that includes the probe ID, CDN,
# hostname, timestamp, average latency, and total loss

async def collect_metrics(targets, probe_id):
    all_results = []

    for cdn, hostname in targets.items():
        try:
            print(f"\nProcessing {hostname}...")
            # Get all IPv4 addresses for the hostname
            addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
            # Extract unique IP addresses
            ip_addresses = list(set(addr[4][0] for addr in addresses))
            print(f"Found IP addresses: {ip_addresses}")

            timestamp = datetime.utcnow().isoformat() + 'Z'

            results = await async_multiping(ip_addresses, count=5, privileged=False)

            # We're going to calculate the mean of the median values, and the overall loss
            median_values = []
            num_results = 0
            loss_tally = 0

            for result in results:
                median_values.append(median(result.rtts))
                num_results += 1
                loss_tally += result.packet_loss

            average_latency = mean(median_values)
            total_loss = loss_tally / num_results

            print("The probe ID is", probe_id)
            print("The average latency is", average_latency)
            print("The overall loss is", total_loss)
            print("The timestamp for this result will be", timestamp)

            results_tuple = (probe_id, timestamp, cdn, hostname, average_latency, total_loss)
            all_results.append(results_tuple)


        except Exception as e:
            print(f"Error processing {hostname}: {str(e)}")
            continue

    return all_results


async def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    if "PROBE-ID" not in config:
        raise ValueError("No PROBE-ID section found in config.ini")
    
    if "TARGETS" not in config:
        raise ValueError("No TARGETS section found in config.ini")

    probe_id = config.get("PROBE-ID", "probe-id")
    
    targets = dict(config["TARGETS"])
    print("Loaded targets:", targets)

    # Collect and print results
    results = await collect_metrics(targets, probe_id)
    
    print("The value returned by the collect_metrics function looks like", results)
    print("The type of the value returned by the collect_metrics function is", type(results))
    print("The member methods of the value returned by the collect_metrics functdion are", dir(results))
    


if __name__ == "__main__":
    asyncio.run(main())




