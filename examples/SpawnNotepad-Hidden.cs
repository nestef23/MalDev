using System;
using System.Diagnostics;

class Program 
{
	static void Main() 
	{
		ProcessStartInfo ProcInfo = new ProcessStartInfo();
		ProcInfo.FileName = "Notepad.exe";
		ProcInfo.WindowStyle = ProcessWindowStyle.Hidden;
		Process.Start(ProcInfo);
		Console.WriteLine("Press any key to exit.");
		Console.ReadKey();
	}
}
