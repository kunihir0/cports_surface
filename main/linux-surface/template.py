pkgname = "linux-surface"
# For master branch builds, manually update pkgver to current date (e.g., YYYYMMDD)
# when you want to package a new snapshot.
pkgver = "20240524" # MANUALLY UPDATE THIS DATE FOR NEW BUILDS
pkgrel = 0
archs = ["x86_64"]
build_style = "linux-kernel"
configure_args = ["FLAVOR=surface", f"RELEASE={pkgrel}"] # Assumes files/surface.config exists
# make_dir = "build" # Let the linux-kernel style handle build directory, or build in-tree.
# ZSTD_CLEVEL for module compression, can be adjusted
make_install_env = {"ZSTD_CLEVEL": "9"}

hostmakedepends = ["base-kernel-devel"] # git, perl, python, xz, etc. are in base-kernel-devel
depends = ["base-kernel"]
provides = ["linux"] # Provides a generic "linux"

pkgdesc = "Linux kernel with linux-surface patches"
subdesc = "master branch"
license = "GPL-2.0-only"
url = "https://github.com/linux-surface/linux-surface"
source = f"https://codeload.github.com/linux-surface/linux-surface/zip/refs/heads/master#/{pkgname}-{pkgver}.zip"
sha256 = "SKIP" # Replace with actual checksum after first fetch

# Options similar to linux-stable, adjust as needed
options = [
    "!check",       # Kernel checks are extensive and often not run in packaging
    "!debug",       # Debug info is typically stripped into a -dbg package
    "!strip",       # Stripping is handled by cbuild for the main package
    "!scanrundeps", # Kernel dependencies are usually well-defined or internal
    "!scanshlibs",  # Kernel doesn't provide shlibs in the typical sense
    "!lto",         # LTO for kernels can be complex, enable if tested
    "textrels",     # Some kernel components might have textrels
    "execstack",    # Potentially needed for some kernel parts
    "foreignelf",   # e.g., for vdso32
]

make_env = {
    "KBUILD_BUILD_HOST": "chimera-linux",
    "KBUILD_BUILD_USER": pkgname,
    "HOSTCC": "clang",
    "CC": "clang",
    "LD": "ld.lld",
    "AR": "llvm-ar",
    "NM": "llvm-nm",
    "OBJCOPY": "llvm-objcopy",
    "OBJDUMP": "llvm-objdump",
}

# Precautionary empty pre_configure to avoid potential upstream script issues
def pre_configure(self):
    # This empty function overrides the default pre_configure behavior
    # to prevent the system script with the faulty self.do(stdout_to_file=...)
    # from running for this package.
    # The main kernel patch (e.g., patch-X.Y.Z.xz) should ideally be handled
    # by cbuild's standard mechanisms if sourced correctly or applied
    # through other means if necessary (e.g. within prepare() if it were a local file).
    self.log(f"Skipping default pre_configure for {self.pkgname} to avoid potential stdout_to_file error.")
    pass

# The linux-kernel build style should handle prepare, build, and install.
# If specific pre-build source manipulation (beyond standard patching via patches/)
# or post-install steps are needed, you can define prepare(), build(), install() here.

@subpackage(f"{pkgname}-devel")
def _(self):
    self.pkgdesc = "Linux kernel with linux-surface patches" # Explicitly set
    self.subdesc = "development files (master branch)"
    self.depends += ["clang", "pahole"] # Common kernel-devel dependencies
    self.options = ["foreignelf", "execstack", "!scanshlibs"]
    # The linux-kernel build style should populate these correctly.
    # Using a glob for the kernel release directory is safer.
    return ["usr/src", "usr/lib/modules/*/build"]

@subpackage(f"{pkgname}-dbg", self.build_dbg)
def _(self):
    self.pkgdesc = "Linux kernel with linux-surface patches" # Explicitly set
    self.subdesc = "debug symbols (master branch)"
    self.options = [
        "!scanrundeps",
        "!strip", # Don't strip the -dbg package itself
        "!scanshlibs",
        "foreignelf",
        "execstack",
        "textrels",
    ]
    # Paths for debug symbols, System.map might need versioning from KERNELRELEASE.
    # Using a glob for the kernel release directory is safer.
    return ["usr/lib/debug", "usr/lib/modules/*/apk-dist/boot/System.map-*"]