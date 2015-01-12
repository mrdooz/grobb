#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parse_base.hpp"
#include "input_buffer.hpp"
#include "gen/demo_base.types.hpp"
#include "gen/demo_base.parse.hpp"

using namespace test;

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
    int a = 10;
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
