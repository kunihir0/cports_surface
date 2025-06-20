pkgname = "linux-surface"
# Choose a base vanilla kernel version you want to use
_base_kernel_ver = "6.14.5"  # EXAMPLE: Replace with a recent stable kernel version matching available Surface patches
pkgver = _base_kernel_ver   # Your package version will be based on this
pkgrel = 0
archs = ["x86_64"]
build_style = "linux-kernel"
# FLAVOR=surface assumes main/linux-surface/files/surface.config exists
# Patches from main/linux-surface/patches/ for _base_kernel_ver should be applied by the build style.
configure_args = ["FLAVOR=surface", f"RELEASE={pkgrel}"]
make_dir = "build" # Common for linux-kernel style
make_install_env = {"ZSTD_CLEVEL": "9"}

hostmakedepends = ["base-kernel-devel"]
depends = ["base-kernel"]
provides = ["linux"]

pkgdesc = "Linux kernel with linux-surface patches"
subdesc = f"based on v{_base_kernel_ver}" # Clarify base
license = "GPL-2.0-only"
url = "https://github.com/linux-surface/linux-surface" # Upstream patchset URL
# Source the vanilla kernel tarball
source = f"https://cdn.kernel.org/pub/linux/kernel/v{_base_kernel_ver[0]}.x/linux-{_base_kernel_ver}.tar.xz#/{pkgname}-base-{_base_kernel_ver}.tar.xz"
sha256 = "SKIP" # MUST be updated after fetching the vanilla kernel source

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
    self.log(f"Skipping default pre_configure for {self.pkgname} to avoid potential stdout_to_file error.")
    self.log(f"Listing contents of {self.chroot_cwd} before configure phase:")
    self.do("ls", "-alph", self.chroot_cwd)
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