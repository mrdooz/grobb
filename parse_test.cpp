#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "gen/parse_base.hpp"
#include "gen/input_buffer.hpp"
#include "gen/demo_base.types.hpp"
#include "gen/demo_base.parse.hpp"
#include "parse_types.hpp"

using namespace test;
using namespace std;

namespace test 
{
struct OutputBuffer
{
  OutputBuffer() : _ofs(0), _capacity(32), _buf(_capacity) {}

  void EnsureCapacity(size_t required)
  {
    if (_capacity - _ofs < required)
    {
      size_t newSize = 2 * max(required, _capacity);
      _buf.resize(newSize);
      _capacity = newSize;
    }
  }

  char* Cur()
  {
    return _buf.data() + _ofs;
  }

  size_t _ofs;
  size_t _capacity;
  vector<char> _buf;
};

void WriteBool(OutputBuffer& buffer, int indent, const char* member, bool value)
{
  buffer.EnsureCapacity(strlen(member) + indent + 16);
  buffer._ofs += sprintf(buffer.Cur(), "%*s: %s;\n", indent, member, value ? "true" : false);
}

void WriteInt(OutputBuffer& buffer, int indent, const char* member, int value)
{
  buffer.EnsureCapacity(strlen(member) + indent + 32);
  buffer._ofs += sprintf(buffer.Cur(), "%s: %d;\n", member, value);
}

void WriteFloat(OutputBuffer& buffer, int indent, const char* member, float value)
{
  buffer.EnsureCapacity(strlen(member) + indent + 32);
  buffer._ofs += sprintf(buffer.Cur(), "%s: %f;\n", member, value);
}

void WriteMsg1(OutputBuffer& buffer,int indent, const Msg1& msg)
{
  buffer._ofs += sprintf(buffer.Cur(), "%*s", indent, "{\n");
  WriteBool(buffer, 4, "m1", msg.m1);

  buffer._ofs += sprintf(buffer.Cur(), "};\n");
}

}


int main(int argc, const char** argv)
{
//   struct Msg1
//   {
//     bool m1;
//     bool m1v;
//     int m2;
//     int m2v;
//     float m3;
//     float m3v;
//     string m4;
//     string m4v;
//     vec2 aa1;
//     vec2 aa1v;
//   };

  const char* t = "{\n\t m1: true; m1v: [false]; m2: 10; m2v: [20, 30, 40]; m3: 1.23; m3v: [.42, 1.23, 4.56]; m4: 'hej'; m4v: ['a', 'b', 'ray']; aa1: { .23, 42.1 }; aa1v: [{ .23, 42.1 }, { 1.23, 142.1 }]; }";
  InputBuffer buf;
  buf._buf = t;
  buf._len = strlen(t);

  Msg1 m;
  if (ParseMsg1(buf, &m))
  {
    printf("parse ok\n");
    OutputBuffer b;
    WriteMsg1(b, 0, m);
    printf("%s\n", string(b._buf.data(), b._ofs).c_str());
  }
  else
  {
    printf("parse failed\n");
  }

/*
  int res = -1;
  ParseInt(buf, &res);
  buf.SkipWhitespace();
  ParseInt(buf, &res);

  printf("%d\n", res);
*/

  return 0;
}
