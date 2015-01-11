#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "parse_base.hpp"
#include "input_buffer.hpp"

struct EffectBase
{
  string factory;
  int start;
  int end;
};

struct Msg1
{
  bool m1;
  vector<bool> m1v;
  int m2;
  vector<int> m2v;
  float m3;
  vector<float> m3v;
  string m4;
  vector<string> m4v;
  vec2 aa1;
  vector<vec2> aa1v;
};

struct Msg2
{
  Msg1 aa;
  mat2 bb;
};

struct Effect1
{
  string factory;
  int start;
  int end;
  int param1;
  float param2;
};

struct Demo
{
  int length;
};


#include "parse_base.hpp"

bool ParseEffectBase(InputBuffer& buf, EffectBase* res)
{
  CHECKED_OP(buf.Expect('{'));

  string id;
  while (true)
  {
    buf.SkipWhitespace();
    // check for a closing tag
    bool end;
    if (buf.ConsumeIf('}', &end) && end)
      break;

    CHECKED_OP(ParseIdentifier(buf, &id));
    buf.SkipWhitespace();

    if (id == "factory")
    {
      CHECKED_OP(ParseString(buf, &res->factory));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "start")
    {
      CHECKED_OP(ParseInt(buf, &res->start));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "end")
    {
      CHECKED_OP(ParseInt(buf, &res->end));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
  }

  return true;
};

bool ParseMsg1(InputBuffer& buf, Msg1* res)
{
  CHECKED_OP(buf.Expect('{'));

  string id;
  while (true)
  {
    buf.SkipWhitespace();
    // check for a closing tag
    bool end;
    if (buf.ConsumeIf('}', &end) && end)
      break;

    CHECKED_OP(ParseIdentifier(buf, &id));
    buf.SkipWhitespace();

    if (id == "m1")
    {
      CHECKED_OP(ParseBool(buf, &res->m1));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "m1v")
    {
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect('['));

      while (true)
      {
        buf.SkipWhitespace();

        // check for the closing ']'
        bool closing;
        CHECKED_OP(buf.ConsumeIf(']', &closing));
        if (closing)
          break;

        // parse the value
        bool value;
        CHECKED_OP(ParseBool(buf, &value));
        res->m1v.push_back(value);

        buf.SkipWhitespace();
        CHECKED_OP(buf.ConsumeIf(',', nullptr));
      }
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));

    }
    if (id == "m2")
    {
      CHECKED_OP(ParseInt(buf, &res->m2));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "m2v")
    {
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect('['));

      while (true)
      {
        buf.SkipWhitespace();

        // check for the closing ']'
        bool closing;
        CHECKED_OP(buf.ConsumeIf(']', &closing));
        if (closing)
          break;

        // parse the value
        int value;
        CHECKED_OP(ParseInt(buf, &value));
        res->m2v.push_back(value);

        buf.SkipWhitespace();
        CHECKED_OP(buf.ConsumeIf(',', nullptr));
      }
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));

    }
    if (id == "m3")
    {
      CHECKED_OP(ParseFloat(buf, &res->m3));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "m3v")
    {
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect('['));

      while (true)
      {
        buf.SkipWhitespace();

        // check for the closing ']'
        bool closing;
        CHECKED_OP(buf.ConsumeIf(']', &closing));
        if (closing)
          break;

        // parse the value
        float value;
        CHECKED_OP(ParseFloat(buf, &value));
        res->m3v.push_back(value);

        buf.SkipWhitespace();
        CHECKED_OP(buf.ConsumeIf(',', nullptr));
      }
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));

    }
    if (id == "m4")
    {
      CHECKED_OP(ParseString(buf, &res->m4));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "m4v")
    {
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect('['));

      while (true)
      {
        buf.SkipWhitespace();

        // check for the closing ']'
        bool closing;
        CHECKED_OP(buf.ConsumeIf(']', &closing));
        if (closing)
          break;

        // parse the value
        string value;
        CHECKED_OP(ParseString(buf, &value));
        res->m4v.push_back(value);

        buf.SkipWhitespace();
        CHECKED_OP(buf.ConsumeIf(',', nullptr));
      }
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));

    }
    if (id == "aa1")
    {
      CHECKED_OP(ParseVec2(buf, &res->aa1));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "aa1v")
    {
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect('['));

      while (true)
      {
        buf.SkipWhitespace();

        // check for the closing ']'
        bool closing;
        CHECKED_OP(buf.ConsumeIf(']', &closing));
        if (closing)
          break;

        // parse the value
        vec2 value;
        CHECKED_OP(ParseVec2(buf, &value));
        res->aa1v.push_back(value);

        buf.SkipWhitespace();
        CHECKED_OP(buf.ConsumeIf(',', nullptr));
      }
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));

    }
  }

  return true;
};

bool ParseMsg2(InputBuffer& buf, Msg2* res)
{
  CHECKED_OP(buf.Expect('{'));

  string id;
  while (true)
  {
    buf.SkipWhitespace();
    // check for a closing tag
    bool end;
    if (buf.ConsumeIf('}', &end) && end)
      break;

    CHECKED_OP(ParseIdentifier(buf, &id));
    buf.SkipWhitespace();

    if (id == "aa")
    {
      CHECKED_OP(ParseMsg1(buf, &res->aa));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "bb")
    {
      CHECKED_OP(ParseMat2(buf, &res->bb));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
  }

  return true;
};

bool ParseEffect1(InputBuffer& buf, Effect1* res)
{
  CHECKED_OP(buf.Expect('{'));

  string id;
  while (true)
  {
    buf.SkipWhitespace();
    // check for a closing tag
    bool end;
    if (buf.ConsumeIf('}', &end) && end)
      break;

    CHECKED_OP(ParseIdentifier(buf, &id));
    buf.SkipWhitespace();

    if (id == "factory")
    {
      CHECKED_OP(ParseString(buf, &res->factory));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "start")
    {
      CHECKED_OP(ParseInt(buf, &res->start));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "end")
    {
      CHECKED_OP(ParseInt(buf, &res->end));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "param1")
    {
      CHECKED_OP(ParseInt(buf, &res->param1));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
    if (id == "param2")
    {
      CHECKED_OP(ParseFloat(buf, &res->param2));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
  }

  return true;
};

bool ParseDemo(InputBuffer& buf, Demo* res)
{
  CHECKED_OP(buf.Expect('{'));

  string id;
  while (true)
  {
    buf.SkipWhitespace();
    // check for a closing tag
    bool end;
    if (buf.ConsumeIf('}', &end) && end)
      break;

    CHECKED_OP(ParseIdentifier(buf, &id));
    buf.SkipWhitespace();

    if (id == "length")
    {
      CHECKED_OP(ParseInt(buf, &res->length));
      buf.SkipWhitespace();
      CHECKED_OP(buf.Expect(';'));
    }
  }

  return true;
};

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
