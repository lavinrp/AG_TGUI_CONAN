import os, shutil
from conans import ConanFile, CMake, tools

class PackagerTGUI(ConanFile):
    name = 'tgui'
    version = '0.8'
    branch = 'stable'
    settings = 'os', 'compiler', 'arch', 'build_type'
    options = {'shared': [True, False], 'cpp17': [True, False]}
    default_options = 'shared=True', 'cpp17=False'
    generators = 'cmake'
    license = 'zlib/png'
    url='https://github.com/texus/TGUI'
    exports = ['CMakeLists.txt']
    requires = "sfml/2.5.0@bincrafters/stable"
    so_version = '0.8'

    _source_subfolder = 'source_subfolder'
    _build_subfolder = 'build_subfolder'

    def source(self):
        self.run("git clone https://github.com/texus/TGUI.git")
        self.run("cd TGUI && git checkout 0.8 && cd ..")
        # its in source/tgui/CMakeLists.txt
        print(os.getcwd())
        os.listdir(os.getcwd())

        # replace use of sfml
        include_sfml_str0 = "if(DEFINED SFML_LIBRARIES)"
        include_sfml_str1 = "    # SFML found via FindSFML.cmake"
        include_sfml_str2 = "    target_include_directories(tgui PRIVATE ${SFML_INCLUDE_DIR})"
        include_sfml_str3 = "    target_link_libraries(tgui PRIVATE ${SFML_LIBRARIES} ${SFML_DEPENDENCIES})"
        include_sfml_str4 = "else()"
        include_sfml_str5 = "    # SFML found via SFMLConfig.cmake"
        include_sfml_str6 = "    target_link_libraries(tgui PRIVATE sfml-graphics)"
        include_sfml_str7 = "endif()"
        include_sfml_str_array = [include_sfml_str0, include_sfml_str1, include_sfml_str2, include_sfml_str3, include_sfml_str4, include_sfml_str5, include_sfml_str6, include_sfml_str7]
        combined_sfml_include_string = ""
        for include_sfml_string in include_sfml_str_array:
            combined_sfml_include_string += include_sfml_string
            if os.name == "nt":
                combined_sfml_include_string += "\r\n"
            else:
                combined_sfml_include_string += "\n"
        conan_include_string = "include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)\r\nconan_basic_setup()\r\ntarget_link_libraries(tgui ${CONAN_LIBS})"

        tools.replace_in_file("./TGUI/src/TGUI/CMakeLists.txt", combined_sfml_include_string, conan_include_string)

        # remove use of find_package for sfml
        str1 = "if(TGUI_OS_WINDOWS AND TGUI_COMPILER_MSVC) # Also look for the main component when using Visual Studio"
        str2 = "    find_package(SFML 2 COMPONENTS main graphics window system)"
        str3 = "elseif(TGUI_OS_ANDROID)  # Search for SFML in the android NDK (if no other directory is specified)"
        str4 = '    find_package(SFML 2 COMPONENTS graphics window system PATHS "${CMAKE_ANDROID_NDK}/sources/third_party/sfml/lib/${CMAKE_ANDROID_ARCH_ABI}/cmake/SFML")'
        str5 = "elseif(TGUI_OS_IOS)  # Use the find_host_package macro from the toolchain on iOS"
        str6 = "    find_host_package(SFML 2 COMPONENTS main graphics window system)"
        str7 = "else()"
        str8 = "    find_package(SFML 2 COMPONENTS graphics window system)"
        str9 = "endif()"
        str10 = ""
        str11 = "# find_package couldn't find SFML"
        str12 = "if(NOT SFML_FOUND)"
        str13 = '    set(SFML_DIR "" CACHE PATH "Path to SFMLConfig.cmake")'
        str14 = '    set(SFML_ROOT "" CACHE PATH "SFML root directory")'
        str15 = '    message(FATAL_ERROR "CMake couldn\'t find SFML.\\nEither set SFML_DIR to the directory containing SFMLConfig.cmake or set the SFML_ROOT entry to SFML\'s root directory (containing \\"include\\" and \\"lib\\" directories).")'
        str16 = "endif()"
        strs = [str1, str2, str3, str4, str5, str6, str7, str8, str9, str10, str11, str12, str13, str14, str15, str16]
        
        find_sfml_string = ""
        for string in strs:
            find_sfml_string += string + "\r\n"
        
        tools.replace_in_file("./TGUI/CMakeLists.txt", find_sfml_string, "" )

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            with tools.vcvars(self.settings, force=True, filter_known_paths=False):
                cmake = self.configure_cmake()
        else:
            cmake = self.configure_cmake()
        self.build_folder = os.getcwd() + "/TGUI"
        cmake.build()

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["TGUI_SHARED_LIBS"] = self.options.shared
        if self.options.shared:
            cmake.definitions["BUILD_SHARED_LIBS"] = "ON"
            cmake.definitions["BUILD_STATIC_LIBS"] = "OFF"
        else:
            cmake.definitions["BUILD_SHARED_LIBS"] = "OFF"
            cmake.definitions["BUILD_STATIC_LIBS"] = "ON"
        if self.options.cpp17:
            cmake.definitions["TGUI_USE_CPP17"] = True

        #os.rename(self._source_subfolder + '/extlibs', self._source_subfolder + '/ext')
        #cmake.configure(build_folder=self._build_subfolder)
        #os.rename(self._source_subfolder + '/ext', self._source_subfolder + '/extlibs')

        self.run("cd ./TGUI")
        print(os.getcwd())
        input("about to configure")
        self.source_folder = os.getcwd() + "/TGUI"
        cmake.configure()
        self.run("cd ..")

        return cmake

    def add_libraries_from_pc(self, library, static=None):
        if static is None:
            static = not self.options.shared
        pkg_config = tools.PkgConfig(library, static=static)
        libs = [lib[2:] for lib in pkg_config.libs_only_l]  # cut -l prefix
        lib_paths = [lib[2:] for lib in pkg_config.libs_only_L]  # cut -L prefix
        self.cpp_info.libs.extend(libs)
        self.cpp_info.libdirs.extend(lib_paths)
        self.cpp_info.sharedlinkflags.extend(pkg_config.libs_only_other)
        self.cpp_info.exelinkflags.extend(pkg_config.libs_only_other)

    def package(self):
        # self.copy(pattern='License.md', dst='licenses', src=self._source_subfolder)
        self.copy('*.*', 'include', 'install/include', keep_path=True)
        self.copy(pattern='*.a', dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.so.' + self.so_version, dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.lib', dst='lib', src='install/lib', keep_path=False)
        self.copy(pattern='*.dll', dst='bin', src='install/lib', keep_path=False)

    def package_info(self):
        if (not self.settings.os == 'Windows') and self.options.shared:
            self.cpp_info.libs = [':libtgui'
                                  + ('-d' if self.settings.build_type == 'Debug' else '')
                                  + '.so.'
                                  + self.so_version]
        else:
            self.cpp_info.libs = ['tgui'
                                  + ('' if self.options.shared else '-s')
                                  + ('-d' if self.settings.build_type == 'Debug' else '')]

