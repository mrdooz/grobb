#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <algorithm>
#include "gen/parse_base.hpp"
#include "gen/input_buffer.hpp"
#include "gen/output_buffer.hpp"
#include "gen/demo_base.types.hpp"
#include "gen/demo_base.parse.hpp"
#include "gen/demo_base.compare.hpp"
#include "parse_types.hpp"

using namespace test;
using namespace std;

#pragma warning(disable: 4996)

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

  bool parseOk = false;
  bool parse2Ok = false;
  bool cmpOk = false;

  Msg1 m;
  parseOk = ParseMsg1(buf, &m);
  if (parseOk)
  {
    OutputBuffer b;
    Serialize(b, m);
    printf("%s\n", string(b._buf.data(), b._ofs).c_str());

    Msg1 m2;
    InputBuffer buf2;
    buf2._buf = b._buf.data();
    buf2._len = b._ofs;
    parse2Ok = ParseMsg1(buf2, &m2);
    if (parse2Ok)
    {
      cmpOk = m == m2;
    }
  }

  printf("parse: %s, parse2: %s, cmp: %s\n", parseOk ? "Y" : "N", parse2Ok ? "Y" : "N", cmpOk ? "Y" : "N");
  {
    OutputBuffer b;
    Msg3 mx, mx2;
    bool tmp = mx == mx2;
    Serialize(b, mx);
    printf("%s\n", string(b._buf.data(), b._ofs).c_str());

    Msg3 m2;
    InputBuffer buf;
    buf._buf = b._buf.data();
    buf._len = b._ofs;
    parse2Ok = ParseMsg3(buf, &m2);
    printf("msg2: %s\n", parse2Ok ? "Y" : "N");
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
