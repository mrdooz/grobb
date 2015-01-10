#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct InputBuf
{
	InputBuf() : buf(nullptr), idx(0), len(0) {}
	InputBuf(const char* buf, size_t len): buf(buf), idx(0), len(len) {}

	bool Peek(char* res)
	{
		if (Eof())
			return false

		*res = buf[idx];
		return true;
	}

	bool Consume()
	{
		if (Eof())
			return false;

		++idx;
		return true;
	}

	bool Eof() {
		return idx == len;
	}

	const char* buf;
	size_t idx;
	size_t len;
};

bool OneOf(InputBuf& buf, const char* str, size_len, int* res)
{
  char ch;
  if (!Peek(res))
    return false;

  *res = -1;
  for (size_t i = 0; i < len; ++i)
  {
    if (ch == str[i])
    {
      Consume();
      *res = i;
      break;
    }
  }

  return true;
}

#define CHECKED_CONSUME() if (!buf.Consume()) { return false; }

bool ParseInt(InputBuf& buf, int* res)
{
	int val = 0;
	char ch;
	if (!buf.Peek(&ch))
		return false;

  bool neg = ch == '-';
  if (neg)




	if (buf.Peek() == '-') 
	{
		neg = true;
		CHECKED_CONSUME();
	}

	char ch = buf.Peek();

	while (true)
	{
		char ch = buf.Peek();
		return true;
	}

	return false;
}

int main(int argc, const char** argv)
{
	const char* t = "20";
	InputBuf buf;
	buf.buf = t;
	buf.len = strlen(t);

	int res = -1;
	ParseInt(buf, &res);

	printf("%d\n", res);

	return 0;
}