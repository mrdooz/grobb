#pragma once
#include "..\parse_types.hpp"

namespace test {

struct InputBuffer;
struct OutputBuffer;

struct vec2
{
  vec2() {}
  vec2(float x, float y) : x(x), y(y) {}
  float x, y;
};

struct vec3
{
  vec3(float x, float y, float z) : x(x), y(y), z(z) {}
  float x, y, z;
};

struct mat2
{
  mat2() {}
  mat2(float m00, float m01, float m10, float m11) : m00(m00), m01(m01), m10(m10), m11(m11) {}
  float m00, m01;
  float m10, m11;
};

bool ParseBool(InputBuffer& buf, bool* res);
bool ParseFloat(InputBuffer& buf, float* res);
bool ParseVec2(InputBuffer& buf, vec2* res);
bool ParseMat2(InputBuffer& buf, mat2* res);
bool ParseInt(InputBuffer& buf, int* res);
bool ParseString(InputBuffer& buf, string* res);
bool ParseIdentifier(InputBuffer& buf, string* res);

void Serialize(OutputBuffer& buffer, int indent, const char* member, bool value);
void Serialize(OutputBuffer& buffer, int indent, const char* member, int value);
void Serialize(OutputBuffer& buffer, int indent, const char* member, float value);
void Serialize(OutputBuffer& buffer, int indent, const char* member, const string& value);
void Serialize(OutputBuffer& buffer, int indent, const char* member, const vec2& value);
void Serialize(OutputBuffer& buffer, int indent, const char* member, const mat2& value);

template <typename T>
void Serialize(OutputBuffer& buffer, int indent, const char* member, const vector<T>& value)
{

}

}
