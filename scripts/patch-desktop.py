#!/usr/bin/env python3
"""Apply the small native window-system portability patch to pinned PS2 Web Recomp.

The upstream native runner currently creates WebGPU surfaces only for X11 and
Wayland. This patch adds Metal and Win32 surfaces and removes Linux-only process
metrics from the Windows compile path. It deliberately fails closed if upstream
source changed unexpectedly.
"""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: patch-desktop.py PATH_TO_PS2_WEB_RECOMP")

root = Path(sys.argv[1]).resolve()

def replace_once(rel, old, new):
    path = root / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{rel}: expected one patch anchor, found {count}: {old[:90]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(
    "runtime/include/ps2/system.hpp",
    "enum Kind { X11, Wayland, Canvas } kind = X11;",
    "enum Kind { X11, Wayland, Metal, Win32, Canvas } kind = X11;"
)
replace_once(
    "runtime/src/gs/gpu/gpu.hpp",
    "enum Kind { X11, Wayland, Canvas } kind;",
    "enum Kind { X11, Wayland, Metal, Win32, Canvas } kind;"
)

replace_once(
    "host/window.cpp",
    '#include <SDL.h>\n#include <SDL_syswm.h>\n#include <sys/resource.h>\n#include <unistd.h>\n',
    '#include <SDL.h>\n#include <SDL_syswm.h>\n#if defined(__APPLE__)\n#include <SDL_metal.h>\n#endif\n#if !defined(_WIN32)\n#include <sys/resource.h>\n#include <unistd.h>\n#endif\n'
)
replace_once(
    "host/window.cpp",
    "SDL_Texture *g_texture = nullptr;\n",
    "SDL_Texture *g_texture = nullptr;\n#if defined(__APPLE__)\nSDL_MetalView g_metal_view = nullptr;\n#endif\n"
)
replace_once(
    "host/window.cpp",
    """#if defined(SDL_VIDEO_DRIVER_WAYLAND)
    case SDL_SYSWM_WAYLAND:
        target.kind = ps2::WindowTarget::Wayland;
        target.display = info.info.wl.display;
        target.surface = info.info.wl.surface;
        break;
#endif
    default: return false;
""",
    """#if defined(SDL_VIDEO_DRIVER_WAYLAND)
    case SDL_SYSWM_WAYLAND:
        target.kind = ps2::WindowTarget::Wayland;
        target.display = info.info.wl.display;
        target.surface = info.info.wl.surface;
        break;
#endif
#if defined(__APPLE__)
    case SDL_SYSWM_COCOA:
        g_metal_view = SDL_Metal_CreateView(g_window);
        if (!g_metal_view) return false;
        target.kind = ps2::WindowTarget::Metal;
        target.surface = SDL_Metal_GetLayer(g_metal_view);
        if (!target.surface) return false;
        break;
#endif
#if defined(_WIN32)
    case SDL_SYSWM_WINDOWS:
        target.kind = ps2::WindowTarget::Win32;
        target.window = reinterpret_cast<std::uintptr_t>(info.info.win.window);
        break;
#endif
    default: return false;
"""
)

replace_once(
    "runtime/src/gs/gpu/gpu.cpp",
    """#ifndef __EMSCRIPTEN__
#include <webgpu/wgpu.h>
#endif
""",
    """#ifndef __EMSCRIPTEN__
#include <webgpu/wgpu.h>
#if defined(_WIN32)
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#endif
#endif
"""
)
replace_once(
    "runtime/src/gs/gpu/gpu.cpp",
    """#else
    WGPUSurfaceSourceXlibWindow xlib = WGPU_SURFACE_SOURCE_XLIB_WINDOW_INIT;
    WGPUSurfaceSourceWaylandSurface wayland = WGPU_SURFACE_SOURCE_WAYLAND_SURFACE_INIT;
    if (target.kind == SurfaceTarget::X11) {
        xlib.display = target.display;
        xlib.window = target.window;
        sd.nextInChain = &xlib.chain;
    } else if (target.kind == SurfaceTarget::Wayland) {
        wayland.display = target.display;
        wayland.surface = target.surface;
        sd.nextInChain = &wayland.chain;
    } else {
        return false;
    }
#endif
""",
    """#else
    WGPUSurfaceSourceXlibWindow xlib = WGPU_SURFACE_SOURCE_XLIB_WINDOW_INIT;
    WGPUSurfaceSourceWaylandSurface wayland = WGPU_SURFACE_SOURCE_WAYLAND_SURFACE_INIT;
#if defined(__APPLE__)
    WGPUSurfaceSourceMetalLayer metal = WGPU_SURFACE_SOURCE_METAL_LAYER_INIT;
#endif
#if defined(_WIN32)
    WGPUSurfaceSourceWindowsHWND win_surface = WGPU_SURFACE_SOURCE_WINDOWS_HWND_INIT;
#endif
    if (target.kind == SurfaceTarget::X11) {
        xlib.display = target.display;
        xlib.window = target.window;
        sd.nextInChain = &xlib.chain;
    } else if (target.kind == SurfaceTarget::Wayland) {
        wayland.display = target.display;
        wayland.surface = target.surface;
        sd.nextInChain = &wayland.chain;
#if defined(__APPLE__)
    } else if (target.kind == SurfaceTarget::Metal) {
        metal.layer = target.surface;
        sd.nextInChain = &metal.chain;
#endif
#if defined(_WIN32)
    } else if (target.kind == SurfaceTarget::Win32) {
        win_surface.hinstance = GetModuleHandleW(nullptr);
        win_surface.hwnd = reinterpret_cast<void *>(static_cast<std::uintptr_t>(target.window));
        sd.nextInChain = &win_surface.chain;
#endif
    } else {
        return false;
    }
#endif
"""
)

replace_once(
    "CMakeLists.txt",
    """        target_link_libraries(ps2runtime PUBLIC "${PS2_WGPU_DIR}/lib/libwgpu_native.a" dl pthread m)
        if(APPLE)
            target_link_libraries(ps2runtime PUBLIC "-framework Metal" "-framework QuartzCore" "-framework Foundation" "-framework CoreFoundation" "-framework IOKit" "-framework IOSurface" objc)
        endif()
""",
    """        target_link_libraries(ps2runtime PUBLIC "${PS2_WGPU_DIR}/lib/libwgpu_native.a")
        if(APPLE)
            target_link_libraries(ps2runtime PUBLIC "-framework Metal" "-framework QuartzCore" "-framework Foundation" "-framework CoreFoundation" "-framework IOKit" "-framework IOSurface" objc)
        elseif(WIN32)
            target_link_libraries(ps2runtime PUBLIC ws2_32 userenv bcrypt ole32 oleaut32 shell32 advapi32 d3d12 dxgi dxguid winmm setupapi rpcrt4 gdi32)
        else()
            target_link_libraries(ps2runtime PUBLIC dl pthread m)
        endif()
"""
)

replace_once(
    "host/window.cpp",
    """double process_cpu_seconds() {
    rusage usage{};
    getrusage(RUSAGE_SELF, &usage);
    return static_cast<double>(usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) + static_cast<double>(usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1e6;
}

double resident_mb() {
    long pages = 0, resident = 0;
    if (std::FILE *f = std::fopen("/proc/self/statm", "r")) {
        if (std::fscanf(f, "%ld %ld", &pages, &resident) != 2) resident = 0;
        std::fclose(f);
    }
    return static_cast<double>(resident) * static_cast<double>(sysconf(_SC_PAGESIZE)) / (1024.0 * 1024.0);
}
""",
    """double process_cpu_seconds() {
#if defined(_WIN32)
    // Keep the window HUD portable; Windows process-time telemetry is optional.
    return 0.0;
#else
    rusage usage{};
    getrusage(RUSAGE_SELF, &usage);
    return static_cast<double>(usage.ru_utime.tv_sec + usage.ru_stime.tv_sec) + static_cast<double>(usage.ru_utime.tv_usec + usage.ru_stime.tv_usec) / 1e6;
#endif
}

double resident_mb() {
#if defined(_WIN32)
    return 0.0;
#else
    long pages = 0, resident = 0;
    if (std::FILE *f = std::fopen("/proc/self/statm", "r")) {
        if (std::fscanf(f, "%ld %ld", &pages, &resident) != 2) resident = 0;
        std::fclose(f);
    }
    return static_cast<double>(resident) * static_cast<double>(sysconf(_SC_PAGESIZE)) / (1024.0 * 1024.0);
#endif
}
"""
)


replace_once(
    "runtime/src/iop/libs.cpp",
    "#include <cstdio>\n#include <deque>\n",
    "#include <cstdio>\n#include <cstdlib>\n#include <deque>\n"
)
replace_once(
    "runtime/include/ps2/vu_ops.hpp",
    "    const v4i clamped = __builtin_elementwise_min((v4i)(x & 0x7FFFFFFFu), (v4i){0x7F7FFFFF, 0x7F7FFFFF, 0x7F7FFFFF, 0x7F7FFFFF});",
    """    const v4i candidate = (v4i)(x & 0x7FFFFFFFu);
    const v4i limit = (v4i){0x7F7FFFFF, 0x7F7FFFFF, 0x7F7FFFFF, 0x7F7FFFFF};
    const v4i below = candidate < limit;
    const v4i clamped = (candidate & below) | (limit & ~below);"""
)
replace_once(
    "runtime/include/ps2/vu_ops.hpp",
    "    if (__builtin_reduce_or((v4i)(x + 0x01000000u > 0x02000000u))) {",
    """    const v4i needs_adjust = (v4i)(x + 0x01000000u > 0x02000000u);
    if (needs_adjust[0] | needs_adjust[1] | needs_adjust[2] | needs_adjust[3]) {"""
)

print("Applied native Metal/Win32 surfaces, libc declarations, and portable vector reductions.")
