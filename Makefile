###############################################################################
#
# Usage:
#    make all               : build all Components
#    make (COMPONENT)       : build a single Component
#    make clean             : clean all Components
#    make clean_(COMPONENT) : clean a single Component
#
###############################################################################



###############################################################################
#
# 1. Compiler and flags
#
###############################################################################

OS := $(shell uname -s)
ifneq (,$(findstring Linux,$(OS)))
export BUILD = UNIX
else
export BUILD = WIN32
endif
export CXX   = gcc
export AR  = ar

ifeq ($(BUILD), UNIX)
export CXXFLAGS = -O2 -std=c++11
else #WIN32
#_USB_CHECK, _DESKTOP_VER, _DEBUG_, _LOG_DECODER_STATS, _DGB_IMEI_CHANGE
export CXXFLAGS = -O1 -march=pentium4 -Wall -Wextra -DWIN32 -DNDEBUG -D_LOG_DECODER_STATS -D_DBG_CORRELATION_
endif

ifeq ($(BUILD), UNIX)
LDFLAGS =  -Wl -m64
else
LDFLAGS =  -Wl,--large-address-aware
endif

###############################################################################
#
# 2. Components and Build Directories
#
###############################################################################
export BASE_DIR = $(CURDIR)
export BUILD_DIR = $(BASE_DIR)

COMPONENTS =  app_gb app_exporter app_importer app_dss ns bssgp llc\
			sndcp tcpip gmm sm sms httpftpwap stub prot_codec app_frm crypto

DLLS = app_dss_component app_flowctrl_component

ifeq ($(BUILD), UNIX)
BOOST_DIR = ../boost_1_57_0
LIBPCAP_DIR = ../framework
LIBUSB_DIR=/usr/lib64
else
BOOST_DIR = $(BASE_DIR)/../../3rd_party/boost/install/boost_1_36_0_mingw3.4.5
LIBPCAP_DIR = $(BASE_DIR)/../../3rd_party/winpcap/WpdPack
endif

INC_DIR = -I$(BOOST_DIR)/include
INC_DIR += -I$(LIBPCAP_DIR)/include

INC_DIR += -I$(BASE_DIR)
INC_DIR += $(patsubst %,-I$(BASE_DIR)/%,$(COMPONENTS)) $(patsubst %,-I$(BASE_DIR)/%,$(DLLS))
INC_DIR += -I$(BASE_DIR)/../voice_quality_monitor/voip-component

export INC_DIR

export COMMON_DEPENDENCES = 

ifeq ($(BUILD), UNIX)
BOOST_SIG_LIB=libboost_signals-mt.a
BOOST_THD_LIB=libboost_thread-mt.a
else
BOOST_SIG_LIB=libboost_signals-mt.lib
BOOST_THD_LIB=libboost_thread-mt.lib
endif

export LIBSENSELOCK_DIR
export LIBUSB_DIR
export LIBICONV_DIR
export BOOST_DIR
export BOOST_SIG_LIB
export BOOST_THD_LIB
###############################################################################
#
# 3. Build target
#
###############################################################################
TARGET = $(BUILD_DIR)/GbDecoder.exe

LIBS = $(patsubst %,-l%,$(notdir $(COMPONENTS)))
DLL_LIBS = $(patsubst %,-l%,$(notdir $(DLLS)))

SRCLIST = $(wildcard *.cpp)
OBJS = $(patsubst %.cpp,$(BUILD_DIR)/objects/%.o,$(SRCLIST))

.PHONY: all $(COMPONENTS) $(DLLS)

all: $(TARGET)

$(TARGET):: $(COMPONENTS) $(DLLS)


ifeq ($(BUILD), UNIX)
$(TARGET):: $(OBJS) $(patsubst -l%,$(BUILD_DIR)/lib/lib%.a, $(LIBS)) $(patsubst -l%,$(BUILD_DIR)/lib/lib%.so, $(DLL_LIBS))
	$(CXX) $(LDFLAGS)  $(OBJS) -o $@ -L$(BUILD_DIR)/lib -Xlinker --start-group -L$(LIBICONV_DIR)/lib $(LIBS) --end-group $(DLL_LIBS)\
            $(LIBPCAP_DIR)/lib/libpcap.a\
            $(BOOST_DIR)/lib/libboost_thread-mt.a\
            $(BOOST_DIR)/lib/libboost_signals-mt.a\
		-lsenselockapi\
                $(LIBUSB_DIR)/libusb-0.1.so.4 \
                $(LIBSENSELOCK_DIR)/libsense4.a \
                 -lpthread -liconv
else
$(TARGET):: $(OBJS) $(patsubst -l%,$(BUILD_DIR)/lib/lib%.a, $(LIBS)) $(patsubst -l%,$(BUILD_DIR)/lib/lib%.dll, $(DLL_LIBS))
	$(CXX) $(LDFLAGS)  $(OBJS) -o $@ -L$(BUILD_DIR)/lib -Xlinker --start-group $(LIBS) --end-group $(DLL_LIBS)\
	    $(BASE_DIR)/../../3rd_party/K15/K12RecFl.lib\
	    $(BASE_DIR)/../../3rd_party/winpcap/WpdPack/Lib/libwpcap.a\
	    $(BASE_DIR)/../../3rd_party/boost/install/boost_1_36_0_mingw3.4.5/lib/libboost_thread-mt.lib\
	    $(BASE_DIR)/../../3rd_party/boost/install/boost_1_36_0_mingw3.4.5/lib/libboost_signals-mt.lib\
	    $(BASE_DIR)/../../product/senselock/release/senselock.lib\
	    "/c/Program Files (x86)/Microsoft Visual Studio 8/VC/PlatformSDK/Lib/WS2_32.Lib"
endif
$(COMPONENTS):
	@echo
	@$(MAKE) -C $@ COMPONENT=$(notdir $(@))
	
$(DLLS):
	@echo
	-@$(MAKE) -C $@ COMPONENT=$(notdir $(@))

$(BUILD_DIR)/objects/%.o: %.cpp %.h $(COMMON_DEPENDENCES)
	@test -d $(BUILD_DIR)/objects || mkdir $(BUILD_DIR)/objects
	$(CXX) $(CXXFLAGS) $(INC_DIR) -c $< -o $@

###############################################################################
#
# 4. Clean
#
###############################################################################
CLEAN_COMPONENTS = $(patsubst %,clean_%,$(COMPONENTS)) $(patsubst %,clean_%,$(DLLS))

.PHONY: clean $(CLEAN_COMPONENTS)

clean: $(CLEAN_COMPONENTS)
	-rm $(OBJS) $(TARGET)

$(CLEAN_COMPONENTS):
	@echo
	-@$(MAKE) -C $(patsubst clean_%,%,$(@)) clean COMPONENT=$(notdir $(patsubst clean_%,%,$(@)))
