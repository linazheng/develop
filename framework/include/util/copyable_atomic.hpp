#ifndef COPYABLE_ATOMIC_HPP_INCLUDED
#define COPYABLE_ATOMIC_HPP_INCLUDED

#include <atomic>

using std::atomic;

namespace zhicloud{

    namespace util{
        template < class T >
        class CopyableAtomic:public atomic< T >{
        public:
            CopyableAtomic():atomic< T >(){
            }
            CopyableAtomic(const CopyableAtomic< T >& other){
                this->store(other.load());
            }
            CopyableAtomic& operator=(const CopyableAtomic< T >& other){
                this->store(other.load());
                return *this;
            }
            CopyableAtomic(const atomic< T >& other){
                this->store(other.load());
            }
            CopyableAtomic& operator=(const atomic< T >& other){
                this->store(other.load());
                return *this;
            }
        };
    }
}

#endif // COPYABLE_ATOMIC_HPP_INCLUDED
