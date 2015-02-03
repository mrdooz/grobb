#pragma once

#include <functional>
#include <string>
#include <vector>

namespace test
{
  using std::string;
  using std::function;
  using std::vector;
}

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

struct vec4
{
  vec4(float x, float y, float z, float w) : x(x), y(y), z(z), w(w) {}
  float x, y, z, w;
};

struct color
{
  color(float x, float y, float z, float w) : x(x), y(y), z(z), w(w) {}
  float x, y, z, w;
};

struct mat2
{
  mat2() {}
  mat2(float m00, float m01, float m10, float m11) : m00(m00), m01(m01), m10(m10), m11(m11) {}
  float m00, m01;
  float m10, m11;
};

inline bool operator==(const vec2& lhs, const vec2& rhs)
{
	return lhs.x == rhs.x && lhs.y == rhs.y;
}

inline bool operator==(const vec3& lhs, const vec3& rhs)
{
  return lhs.x == rhs.x && lhs.y == rhs.y && lhs.z == rhs.z;
}

inline bool operator==(const vec4& lhs, const vec4& rhs)
{
  return lhs.x == rhs.x && lhs.y == rhs.y && lhs.z == rhs.z && lhs.w == rhs.w;
}

inline bool operator==(const color& lhs, const color& rhs)
{
  return lhs.x == rhs.x && lhs.y == rhs.y && lhs.z == rhs.z && lhs.w == rhs.w;
}

inline bool operator==(const mat2& lhs, const mat2& rhs)
{
	return lhs.m00 == rhs.m00 && lhs.m01 == rhs.m01 && lhs.m10 == rhs.m10 && lhs.m11 == rhs.m11;
}
