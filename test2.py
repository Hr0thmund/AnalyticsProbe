import configparser
import asyncio
import socket
from icmplib import async_multiping

async def collect_metrics(targets):
    all_results = {}

    for cdn, hostname in targets.items():
        try:
            print(f"\nProcessing {hostname}...")
            # Get all IPv4 addresses for the hostname
            addresses = socket.getaddrinfo(hostname, None, socket.AF_INET, socket.SOCK_STREAM)
            # Extract unique IP addresses
            ip_addresses = list(set(addr[4][0] for addr in addresses))
            print(f"Found IP addresses: {ip_addresses}")


            results = await async_multiping(ip_addresses, count=5, privileged=False)

            for result in results:
                print("The value of result.rtts is", result.rtts)

            # Store results mapped to IP addresses
            all_results[hostname] = {
                str(result.address): result
                for result in results
            }


        except Exception as e:
            print(f"Error processing {hostname}: {str(e)}")
            continue

    return all_results


async def main():
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if 'TARGETS' not in config:
        raise ValueError("No TARGETS section found in config.ini")
    
    targets = dict(config['TARGETS'])
    print("Loaded targets:", targets)

    # Collect and print results
    results = await collect_metrics(targets)
    
    print("The value returned by the collect_metrics function looks like", results)
    print("The type of the value returned blah is", type(results))

#    # Print results in a more readable format
#    print("old/busted:")
#    for hostname, ip_results in results.items():
#        print(f"\nResults for {hostname}:")
#        for ip, ping_results in ip_results.items():
#            print(f"  IP: {ip}")
#            for ping in ping_results:
#                print(f"    RTT: {ping.avg_rtt:.2f}ms")


    # new and improved:
    print("new/hotness:")
    for hostname, ip_results in results.items():
        print(f"\nResults for {hostname}:")
        for ip, ping_result in ip_results.items():
            print(f"  IP: {ip}")
            print(f"    Min RTT: {ping_result.min_rtt:.2f}ms")
            print(f"    Avg RTT: {ping_result.avg_rtt:.2f}ms")
            print(f"    Max RTT: {ping_result.max_rtt:.2f}ms")
            print(f"    Packets sent: {ping_result.packets_sent}")
            print(f"    Packets received: {ping_result.packets_received}")
            print(f"    Packet loss: {ping_result.packet_loss}%")
            print("The attributes returned by the ping function are", dir(ping_result))
            print("The type of ping_result.rtts is ", type(ping_result.rtts))
            print("The value of ping_result.rtts is ", ping_result.rtts)
#            print("What happens if I just print the return directly? Let's see:", ping_result)

if __name__ == "__main__":
    asyncio.run(main())




