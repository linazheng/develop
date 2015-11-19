#include <iostream>
#include "util/serial_test.h"

#include <util/define.hpp>
#include <util/network_utility.h>
#include <util/domain_utility.h>
#include <util/logger.h>
#include <util/logging.h>
#include <iostream>
#include <thread>
#include <chrono>
#include <boost/log/trivial.hpp>

#include <transaction/base_session.hpp>
#include <transaction/base_task.hpp>
#include <transaction/process_rule.hpp>
#include <transaction/base_manager.hpp>
#include <transport/app_message.h>
#include <transport/command.h>


#include <boost/random.hpp>
#include <boost/random/random_device.hpp>
#include <zpl.hpp>

#include <semaphore.h>
#include <time.h>
#include <istream>
#include <vector>

using namespace std;
using namespace zhicloud::transaction;
using namespace zhicloud::transport;
using namespace zhicloud::util;

SerialTest::SerialTest()
{
    //ctor
}

SerialTest::~SerialTest()
{
    //dtor
}
void SerialTest::init()
{
    return;
}

bool SerialTest::test()
{
	try{
		{
			const uint64_t input = 7343478;
			uint64_t output;
			stringstream stream;
		
			Serialize::writeVariant(stream, input);
		
			Serialize::readVariant(stream, output);
			if (input != output)
			{
				BOOST_LOG_TRIVIAL(warning) << boost::format("SerialTest uint64_t stream[%s], output[%d], cmp failed!")
										%stream  %output;
				
                throw std::logic_error("Serialize test writeVariant for u64 failed");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeVariant for u64 passed!";
		}
		{
			const uint32_t input = 43734;
			uint32_t output;
			stringstream stream;

			Serialize::writeVariant(stream, (uint64_t)input);

			Serialize::readVariant(stream, output);
			if (input != output)
			{
				BOOST_LOG_TRIVIAL(warning) << boost::format("SerialTest uint32_t stream[%s], output[%d], cmp failed!")
										%stream  %output;
                throw std::logic_error("Serialize test writeVariant for u32 failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeVariant for u32 passed!";
		}

		
		{
			string input;
			string output;
			stringstream stream;
		
			input = "wangli test writeString";
			Serialize::writeString(stream, input);
		
			Serialize::readString(stream, output);
		
			if (input.compare(output))
			{				
                throw std::logic_error("Serialize test writeString for string failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeString for string passed!";
		}

		
		{
			char buf[] = "asdffdsadfevxcv32356534214t";
			string s2 = (string)buf;
			int size = 15;
			string output;
			stringstream stream;
		
			Serialize::writeString(stream, buf, size);
		
			Serialize::readString(stream, output);
		
			s2 = s2.substr(0, size);
			if ( s2 !=	output)
			{				
                throw std::logic_error("Serialize test writeString for char failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeString for char passed!";
		
		}

		{
			const float input = 64231.57;
			float output;
			stringstream stream;
		
			Serialize::writeFloat(stream, input);
		
			Serialize::readFloat(stream, output);
			if (input != output)
			{
				BOOST_LOG_TRIVIAL(warning) << boost::format("SerialTest float stream[%s], output[%f], cmp failed!")
										%stream  %output;
                throw std::logic_error("Serialize test writeFloat failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeFloat passed!";
		}
		
		{
			const Serialize::ushort_type input = 1274;
			Serialize::ushort_type output;
			stringstream stream;
		
			Serialize::writeShort(stream, input);
		
			Serialize::readShort(stream, output);
			if (input != output)
			{
				BOOST_LOG_TRIVIAL(warning) << boost::format("SerialTest short stream[%s], output[%d], cmp failed!")
										%stream  %output;
                throw std::logic_error("Serialize test writeShort failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeShort passed!";
		}
		{
			const Serialize::ulong_type input = 32768;
			Serialize::ulong_type output;
			stringstream stream;
		
			Serialize::writeLong(stream, input);
		
			Serialize::readLong(stream, output);
			if (input != output)
			{
				BOOST_LOG_TRIVIAL(warning) << boost::format("SerialTest ulong_type stream[%s], output[%d], cmp failed!")
										%stream  %output;
                throw std::logic_error("Serialize test writeLong failed!");
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeLong passed!";
		}
		
		{
			boost::random::mt19937 gen;
			vector< uint64_t > input_array;
			for ( int i = 0 ; i < 5 ; i++ )
			{
				//boost::uniform_int<> real(1, 999);
				input_array.emplace_back(std::move(i*34));
			}
			uint64_t size;
			uint64_t output;
			stringstream stream;
		
			Serialize::writeVariantArray(stream, input_array);
		
			Serialize::readVariant(stream, size);
		
			//BOOST_LOG_TRIVIAL(info) << boost::format("Array size[%d].")%size;
			int i = 0;
			while (size)
			{
				Serialize::readVariant(stream, output);
				BOOST_LOG_TRIVIAL(info) << boost::format("SerialTest writeVariantArray, output[%d].")
										 %output;
		
				if (output != input_array[i])
				{					
					throw std::logic_error("Serialize test writeVariantArray failed!");
				}
				i++;
				size--;
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeVariantArray passed!";
		}

		
		{
			vector< string > input_array;
			for ( int i = 0 ; i < 5 ; i++ )
			{
				input_array.push_back(uuid.uuid());
				//BOOST_LOG_TRIVIAL(info) << boost::format("SerialTest writeStringArray, input[%s].") %input_array[i];
			}
		
			uint64_t size;
			string output;
			stringstream stream;
		
			Serialize::writeStringArray(stream, input_array);
		
			Serialize::readVariant(stream, size);
		
			//BOOST_LOG_TRIVIAL(info) << boost::format("Array size[%d].")%size;
			int i = 0;
			while (size)
			{
				Serialize::readString(stream, output);
				if (output.compare(input_array[i]))
				{					
					throw std::logic_error("Serialize test writeStringArray failed!");
				}
				i++;
				size--;
			}
			BOOST_LOG_TRIVIAL(info) <<"Serialize test writeVariantArray passed!";
			return true;
		}

		
		BOOST_LOG_TRIVIAL(info) <<"Serialize test all passed.";
	}
    catch(exception& ex){
        BOOST_LOG_TRIVIAL(error) << "Serialize test exception:" << ex.what();
        return false;
    }

}





