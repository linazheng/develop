#ifndef GENERATOR_H
#define GENERATOR_H

#include <string>
#include <boost/uuid/uuid.hpp>
#include <boost/uuid/random_generator.hpp>
#include <boost/random.hpp>

using namespace std;
namespace zhicloud{
    namespace util{
        class Generator
        {
            private:
                typedef uniform_int_distribution<unsigned long> distribution_type;
                typedef boost::variate_generator<boost::mt19937&, distribution_type > generator_type;
            public:
                Generator();
                virtual ~Generator();
                string uuid();
                string uuid_hex(bool upper = false);
            private:
                void generateUUID(boost::uuids::uuid& id);
                boost::mt19937 engine;
                distribution_type distribution;
                generator_type generator;
        };
    }
}



#endif // GENERATOR_H
