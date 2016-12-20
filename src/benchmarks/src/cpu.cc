#include <stdio.h> 
#include <stdlib.h>
#include <time.h>
#include <vector>
#include <chrono>
#include <iostream>
#include <fstream>
#include <stdarg.h>
#include <functional>
#include <unistd.h>

#include "libs/json.hpp"
#include "libs/md5.hpp"

#define KB  1024
#define MB  1048576
#define REP (KB * KB)
#define OFFSET 512
#define ARR_SIZE (100 * MB)

#define GIGA  1.0e+9
#define MEGA  1.0e+6
#define KILO  1.0e+3
#define MILI  1.0e-3
#define MICRO 1.0e-6
#define NANO  1.0e-9

#define CHAR_SIZE sizeof(char)
#define INT_SIZE  sizeof(int)

#define SHOW_DURATION true
#define SHOW_DETAILS  true

using namespace std;
using json = nlohmann::json;


static unsigned long x=123456789, y=362436069, z=521288629;

unsigned long random_long(void) {          //period 2^96-1
unsigned long t;
    x ^= x << 16;
    x ^= x >> 5;
    x ^= x << 1;

   t = x;
   x = y;
   y = z;
   z = t ^ x ^ y;

  return z;
}

class Timer {
protected:
    chrono::high_resolution_clock::time_point _start;
    chrono::high_resolution_clock::time_point _stop;
public:
    chrono::duration<double, nano> duration;
    void start() {
        this->_start = std::chrono::high_resolution_clock::now();
    }
    void stop() {
        this->_stop = std::chrono::high_resolution_clock::now();
        this->duration = chrono::duration_cast<chrono::nanoseconds>(this->_stop - this->_start);
    }
};

std::string random_string( size_t length ) {
    auto randchar = []() -> char {
        const char charset[] =
        "0123456789"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "abcdefghijklmnopqrstuvwxyz";
        const size_t max_index = (sizeof(charset) - 1);
        return charset[ random_long() % max_index ];
    };
    std::string str(length,0);
    std::generate_n( str.begin(), length, randchar );
    return str;
}

void printf_debug(const char * fmt, ...) {
    printf("                                          \r");
    string newfmt = string(fmt) + "\r";
    const char * newfmt_c = newfmt.c_str();
    va_list args;
    va_start(args, fmt);
    vprintf(newfmt_c, args);
    va_end(args);
    cout << flush;
}


void reg_simple(json &results, int reps = 100) {
    printf_debug("cpu simple, size=%d, reps=%d", REP, reps);
    Timer timer;
    
    //-------------------------------------------------------
    timer.start();
    int sum;
    for (size_t j = 0; j < reps; j++) {
        for (size_t i = 0; i < REP; i++) {
            sum += random_long();
        }
    }
    timer.stop();
    //-------------------------------------------------------
    results["duration"] = timer.duration.count() * NANO;
    results["size"]     = reps * REP;
}

void reg_hash(json &results, int reps = 100) {
    printf_debug("cpu hash, size=%d, reps=%d", REP, reps);
    Timer timer;
    hash<int> int_hash;
    
    //-------------------------------------------------------
    timer.start();
    string res;
    const int HALF = RAND_MAX / 2;
    for (size_t j = 0; j < reps; j++) {
        for (size_t i = 0; i < REP; i++) {
            res = int_hash(random_long() - HALF);
        }
    }
    timer.stop();
    //-------------------------------------------------------
    results["duration"] = timer.duration.count() * NANO;
    results["size"]     = reps * REP;
}

void reg_md5(json &results, int reps = 1, int str_len = 16) {
    printf_debug("cpu md5, size=%d, reps=%d", REP, reps);
    Timer timer;
    hash<int> str_hash;
    
    //-------------------------------------------------------
    timer.start();
    string res;
    for (size_t j = 0; j < reps; j++) {
        for (size_t i = 0; i < REP; i++) {
            res = md5(random_string(str_len));
        }
    }
    timer.stop();
    //-------------------------------------------------------
    results["duration"] = timer.duration.count() * NANO;
    results["size"]     = reps * REP * str_len;
}

// int* get_mem(json &results, int size = ARR_SIZE) {
//     printf_debug("creating array...         ");
//     static int arr[ARR_SIZE];
//     printf_debug("randomizing array...      ");
//     int sum = 0;
//     int mod = 16-1;
//     
//     static int sizes[] = {
//         // 1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
//         1 * KB, 1 * KB, 1 * KB
//         // 32 * MB, 32 * MB, 32 * MB
//         // 1 * KB, 2 * KB, 4 * KB, 8 * KB, 16 * KB, 32 * KB, 64 * KB, 128 * KB,
//         // 256 * KB, 512 * KB, 1 * MB, 2 * MB, 4 * MB, 8 * MB, 16 * MB, 32 * MB
//         // 4 * KB, 128 * KB, 8 * MB, 32 * MB
//     };
//     
//     for (int i = 0; i < 3; i++) {
//         mod = sizes[i] - 1;
//         for (int j = 0; j < 100*1000; j++) {
//             sum += arr[(j * OFFSET) & mod];
//             // arr[(i * MB + i) & ARR_SIZE] = i;//random_long();
//         }
//     }
//     return arr;
// }

/**
 * Start benchmark, usage:
 * optional <output> file: will create json file output with results
 * optional <scale> float: scales repetition count for benchmark
 *                         default is 1, for example value 2 will run tests 
 *                         twice as many times, value 0.5 will experiments half
 *                         as many times
 */
int main(int argc,  char* argv[]) {
    int rep_cnt = (int)(argc >= 3 ? std::stof(argv[2]) * REP : 1 * REP);
    
    printf_debug("running tests...         ");
    json results;
    
    
    Timer test_timer;
    test_timer.start();
    // ------------------------------------------------------------------------
    get_mem(results["mem"]);
    // reg_simple(results["reg"]["simple"]);
    // reg_hash  (results["reg"]["hash"]);
    // reg_md5   (results["reg"]["md5"]);
    // ------------------------------------------------------------------------
    test_timer.stop();
    printf("---------------------------------\n");
    
    printf("%-30s: %1.3f\n", "time taken", test_timer.duration.count() * NANO);
    
    printf_debug("generating output...    \n");
    cout << results.dump(true) << endl;
    if (argc >= 2) {
        ofstream ofs (argv[1]);
        ofs << results.dump(true) << endl;
    }
    
    return 0;
}