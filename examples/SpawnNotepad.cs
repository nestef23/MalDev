using System;
using System.Diagnostics;

class Program 
{
	static void Main() 
	{
		Process.Start("Notepad.exe");
		Console.WriteLine("Press any key to exit.");
		Console.ReadKey();
	}
}
