// Besed on following blogpost
//https://shubakki.github.io/posts/2022/12/detecting-and-evading-sandboxing-through-time-based-evasion/

#include <windows.h>
#include <iostream>
#include <chrono>
#include <ctime> 
#include <intrin.h>

int main()
{
    long long clock1, clock2 = 0; // setup envs for time tracking

    // ------ CPU CLOCK CYCLES CHECK -------
    std::cout << "Running check 1 \n";
    //start value
    clock1 = __rdtsc();
	auto start1 = std::chrono::system_clock::now();
    // loop a lot of times doing some calculations
    int out[4]; // buffer for cpuidex to write into
	for (int i = 0; i < 10; i++) { 
        for (int j = 0; j < 1000000; j++) {
            // burn some cpu cycles
            __cpuidex( out, 0, 0 ); 
            std::size_t h1 = std::hash<std::string>{}("MyString");
        }
	}
    //end value
    clock2 = __rdtsc();
    auto end1 = std::chrono::system_clock::now();
	
    //check diff
    std::cout << "CPU clock cycles spent on calculations: " << clock2-clock1 << "\n";
    std::chrono::duration<double> elapsed_seconds = end1-start1;
    std::cout << "elapsed time: " << elapsed_seconds.count() << "s \n";
    
    //Virtualization detected
    if (clock2-clock1 > 10000000000 or elapsed_seconds.count() > 3)
        std::cout << "Too long - VM detected! \n";

    // ------ SLEEP CHECK -------
    std::cout << "Running check 2 \n";
    //start values
    clock1 = __rdtsc();
    auto start2 = std::chrono::system_clock::now();
    
    Sleep(5000);
    
    //end values
    clock2 = __rdtsc();
    auto end2 = std::chrono::system_clock::now();

    //check diff
    std::cout << "CPU clock cycles spent sleeping: " << clock2-clock1 << "\n";
    elapsed_seconds = end2-start2;
    std::cout << "elapsed time: " << elapsed_seconds.count() << "s \n";

    if(elapsed_seconds.count() < 4)
        std::cout << "Time warp - Sandboxing detected! \n";
}