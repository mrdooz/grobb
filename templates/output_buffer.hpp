#pragma once
#include "..\parse_types.hpp"

namespace test
{
  struct OutputBuffer
  {
    OutputBuffer();
    void EnsureCapacity(size_t required);
    char* Cur();

    size_t _ofs;
    size_t _capacity;
    vector<char> _buf;
  };
}