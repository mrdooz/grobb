#include <ctype.h>
#include "parse_base.hpp"
#include "input_buffer.hpp"

namespace test {
  //-----------------------------------------------------------------------------
  bool ParseBool(InputBuffer& buf, bool* res)
  {
    size_t start = buf._idx;
    size_t end;
    CHECKED_OP(buf.SkipWhile(InputBuffer::IsAlphaNum, &end));

    string str;
    CHECKED_OP(buf.SubStr(start, end - start, &str));

    if (str == "true")
    {
      *res = true;
      return true;
    }

    if (str == "false")
    {
      *res = false;
      return true;
    }

    return false;
  }

  //-----------------------------------------------------------------------------
  bool ParseFloat(InputBuffer& buf, float* res)
  {
    char ch;
    CHECKED_OP(buf.OneOf("-+", 2, &ch));
    bool neg = ch == '-';

    int whole = 0;
    // find whole part if one exists
    while (true)
    {
      CHECKED_OP(buf.Get(&ch));
      if (!InputBuffer::IsDigit(ch))
      {
        break;
      }
      whole = whole * 10 + (ch - '0');
    }

    float tmp = (neg ? -1.f : 1.f) * whole;

    // If we ended on a '.', parse the fraction
    if (ch == '.')
    {
      // fractional
      int frac = 0;
      int len = 0;
      while (buf.Satifies(InputBuffer::IsDigit, &ch))
      {
        ++len;
        frac = frac * 10 + (ch - '0');
      }

      if (len)
      {
        tmp += frac / powf(10.f, (float)len);
      }
    }

    *res = tmp;
    return true;
  }

  //-----------------------------------------------------------------------------
  bool ParseInt(InputBuffer& buf, int* res)
  {
    char ch;
    CHECKED_OP(buf.OneOf("-+", 2, &ch));
    bool neg = ch == '-';

    // read the first char, and make sure it's a digit
    CHECKED_OP(buf.Satifies(InputBuffer::IsDigit, &ch));

    int val = ch - '0';
    while (buf.Satifies(InputBuffer::IsDigit, &ch))
    {
      val = val * 10 + (ch - '0');
    }

    *res = (neg ? -1 : 1) * val;
    return true;
  }

  //-----------------------------------------------------------------------------
  template<int N>
  bool ParseVec(InputBuffer& buf, float* res)
  {
    // { x, y, z, w }
    CHECKED_OP(buf.Expect('{'));

    for (int i = 0; i < N; ++i)
    {
      buf.SkipWhitespace();
      CHECKED_OP(ParseFloat(buf, &res[i]));

      if (i != N-1)
      {
        buf.SkipWhitespace();
        CHECKED_OP(buf.Expect(','));
      }
    }

    buf.SkipWhitespace();
    CHECKED_OP(buf.Expect('}'));
    return true;
  }

  //-----------------------------------------------------------------------------
  bool ParseVec2(InputBuffer& buf, vec2* res)
  {
    float tmp[2];
    CHECKED_OP(ParseVec<2>(buf, tmp));
    *res = vec2(tmp[0], tmp[1]);
    return true;
  }

  //-----------------------------------------------------------------------------
  bool ParseMat2(InputBuffer& buf, mat2* res)
  {
    // { {a, b}, {c, d} }
    CHECKED_OP(buf.Expect('{'));
    buf.SkipWhitespace();

    float row0[2];
    CHECKED_OP(ParseVec<2>(buf, row0));

    buf.SkipWhitespace();
    CHECKED_OP(buf.Expect(','));

    float row1[2];
    CHECKED_OP(ParseVec<2>(buf, row1));

    buf.SkipWhitespace();
    CHECKED_OP(buf.Expect('}'));

    *res = mat2(row0[0], row0[1], row1[0], row1[1]);
    return true;
  }

  //-----------------------------------------------------------------------------
  bool ParseString(InputBuffer& buf, string* res)
  {
    CHECKED_OP(buf.SkipUntil('\'', true));
    size_t start = buf._idx;
    CHECKED_OP(buf.SkipUntil('\'', true));
    size_t end = buf._idx;
    return buf.SubStr(start, end - start, res);
  }

  //-----------------------------------------------------------------------------
  bool ParseIdentifier(InputBuffer& buf, string* res)
  {
    // an identifier consists of 'id:', so we parse the id, and then find the trailing ':'
    size_t start = buf._idx;
    size_t end;
    CHECKED_OP(buf.SkipWhile(InputBuffer::IsAlphaNum, &end));

    // find the trailing ':'
    CHECKED_OP(buf.SkipUntil(':', true));

    return buf.SubStr(start, end - start, res);
  }

}
