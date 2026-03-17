/*
 * Tutorial 1 (C++): Streaming packets to a DumpFrameFilter
 *
 * Requires the limef .deb package to be installed.
 *
 * Compile:
 *
 *   g++ -std=c++20 \
 *       -I/usr/local/include \
 *       -I/usr/local/include/limef \
 *       -I/usr/local/include/limef/ffmpeg \
 *       t01_mediafile_dump.cpp \
 *       -L/usr/local/lib -lLimef \
 *       -o t01_mediafile_dump
 *
 * Run:
 *
 *   ./t01_mediafile_dump video.mp4
 */

#include <iostream>
#include <thread>
#include <chrono>

#include "limef/framefilter/dump.h"
#include "limef/thread/mediafile.h"

// ── Build the filterchain ─────────────────────────────────────────────────────
// Framefilters are stack-allocated objects.  Connect them with cc() before
// starting the thread.

int main(int argc, char* argv[]) {
    const std::string media_file = (argc > 1) ? argv[1] : "video.mp4";

    Limef::ff::DumpFrameFilter dump("dump");

    // ── Configure the source thread ───────────────────────────────────────────
    // fps = -1: pace packets at the stream's natural playback speed.
    // fps =  0: feed as fast as possible (default).
    // fps =  N: feed at N frames per second.

    Limef::thread::MediaFileContext ctx(media_file, /*slot=*/1);
    ctx.fps = -1;   // natural live speed

    Limef::thread::MediaFileThread thread("reader", ctx);
    thread.getOutput().cc(dump);
    thread.start();

    // ── Let it run, then stop ─────────────────────────────────────────────────
    // stop() sends a stop signal through the pipeline and blocks until done.

    std::cout << "Streaming for 5 seconds — watch the DumpFrameFilter output ..." << std::endl;
    std::this_thread::sleep_for(std::chrono::seconds(5));

    thread.stop();
    std::cout << "Done." << std::endl;
    return 0;
}
