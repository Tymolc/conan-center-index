from conans import ConanFile, tools
import os


class B2Conan(ConanFile):
    name = "b2"
    homepage = "https://boostorg.github.io/build/"
    description = "B2 makes it easy to build C++ projects, everywhere."
    topics = ("conan", "installer", "boost", "builder")
    license = "BSL-1.0"
    settings = "os_build", "arch_build"
    url = "https://github.com/conan-io/conan-center-index"

    '''
    * use_cxx_env: False, True

    Indicates if the build will use the CXX and
    CXXFLAGS environment variables. The common use is to add additional flags
    for building on specific platforms or for additional optimization options.

    * toolset: 'auto', 'cxx', 'cross-cxx',
    'acc', 'borland', 'clang', 'como', 'gcc-nocygwin', 'gcc',
    'intel-darwin', 'intel-linux', 'intel-win32', 'kcc', 'kylix',
    'mingw', 'mipspro', 'pathscale', 'pgi', 'qcc', 'sun', 'sunpro',
    'tru64cxx', 'vacpp', 'vc12', 'vc14', 'vc141', 'vc142'

    Specifies the toolset to use for building. The default of 'auto' detects
    a usable compiler for building and should be preferred. The 'cxx' toolset
    uses the 'CXX' and 'CXXFLAGS' solely for building. Using the 'cxx'
    toolset will also turn on the 'use_cxx_env' option. And the 'cross-cxx'
    toolset uses the 'BUILD_CXX' and 'BUILD_CXXFLAGS' vars. This frees the
    'CXX' and 'CXXFLAGS' variables for use in subprocesses.
    '''
    options = {
        'use_cxx_env': [False, True],
        'toolset': [
            'auto', 'cxx', 'cross-cxx',
            'acc', 'borland', 'clang', 'como', 'gcc-nocygwin', 'gcc',
            'intel-darwin', 'intel-linux', 'intel-win32', 'kcc', 'kylix',
            'mingw', 'mipspro', 'pathscale', 'pgi', 'qcc', 'sun', 'sunpro',
            'tru64cxx', 'vacpp', 'vc12', 'vc14', 'vc141', 'vc142' ]
    }
    default_options = {
        'use_cxx_env': False,
        'toolset': 'auto'
    }

    def configure(self):
        if self.options.toolset == 'cxx' or self.options.toolset == 'cross-cxx':
            self.options.use_cxx_env = True

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "build-" + \
            os.path.basename(self.conan_data["sources"][self.version]['url']).replace(
                ".tar.gz", "")
        os.rename(extracted_dir, "source")

    def build(self):
        use_windows_commands = os.name == 'nt'
        command = "build" if use_windows_commands else "./build.sh"
        if self.options.toolset != 'auto':
            command += " "+str(self.options.toolset)
        build_dir = os.path.join(self.source_folder, "source")
        engine_dir = os.path.join(build_dir, "src", "engine")
        os.chdir(engine_dir)
        with tools.environment_append({"VSCMD_START_DIR": os.curdir}):
            if self.options.use_cxx_env:
                # Allow use of CXX env vars.
                self.run(command)
            else:
                # To avoid using the CXX env vars we clear them out for the build.
                with tools.environment_append({"CXX": "", "CXXFLAGS": ""}):
                    self.run(command)
        os.chdir(build_dir)
        command = os.path.join(
            engine_dir, "b2.exe" if use_windows_commands else "b2")
        full_command = \
            "{0} --ignore-site-config --prefix=../output --abbreviate-paths install".format(
                command)
        self.run(full_command)

    def package(self):
        self.copy("LICENSE.txt", dst="licenses", src="source")
        self.copy(pattern="*b2", dst="bin", src="output/bin")
        self.copy(pattern="*b2.exe", dst="bin", src="output/bin")
        self.copy(pattern="*.jam", dst="bin/b2_src", src="output/share/boost-build")

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.env_info.path = [os.path.join(
            self.package_folder, "bin")] + self.env_info.path
        self.env_info.BOOST_BUILD_PATH = os.path.join(
            self.package_folder, "bin", "b2_src", "src", "kernel")
