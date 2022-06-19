using System;
using System.Diagnostics;

class Program 
{
	static void Main(string[] args)
	{
		// Fun fact: if you spawn powershell.exe -> notepad.exe, the powershell
        // will terminate immediatelly after, so notepad.exe will show as orphaned,
		//but still running process

		//First argument - name of spawned process
		string filename = "Notepad.exe";
		if (args.Length > 0)
			filename = args[0];
		//Second argument - arguments to pass
		string arguments = "";
		if (args.Length > 1)
			arguments = args[1];
		ProcessStartInfo ProcInfo = new ProcessStartInfo();
		ProcInfo.FileName = filename;
		ProcInfo.Arguments = arguments;
		ProcInfo.WindowStyle = ProcessWindowStyle.Hidden;
		Process.Start(ProcInfo);
		Console.WriteLine("Press any key to exit.");
		Console.ReadKey();
	}
}
