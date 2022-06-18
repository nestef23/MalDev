using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;
using System.Net.NetworkInformation;

class Program 
{
	static void Main(string[] args) 
	{
		string domain = "www.google.com";
		if (args.Length > 0)
			domain = args[0];
		try
		{
			Ping ping = new Ping();
			PingReply reply = ping.Send(domain, 1000);
			Console.WriteLine("Ping to:" + domain);
			if (reply != null)
			{
				Console.WriteLine("Ping reply:" + reply.Status + " " + reply.Address);
			}
		}
		catch
		{
			Console.WriteLine("ERROR: You have Some TIMEOUT issue");
		}
		Console.ReadKey();
	}
}
