"""
Application to create .fsproj from much simpler .json

Expected JSON:
{
  "name": "unique project name",
  "output": "binary output folder (optional, ignored by fable)",
  "reference": [
    "referenced .dll file"
  ],
  "compile": [
    "included .fs or .fsx file"
  ]
}
"""

import sys
import json
import uuid
import hashlib
import argparse
import os.path
import xml.sax.saxutils
import tempfile

PROJECT_TEMPLATE = (
r"""<?xml version="1.0" encoding="utf-8"?>
<Project ToolsVersion="12.0" DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Import Project="$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props" Condition="Exists('$(MSBuildExtensionsPath)\$(MSBuildToolsVersion)\Microsoft.Common.props')" />
  <PropertyGroup>
    <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration>
    <Platform Condition=" '$(Platform)' == '' ">AnyCPU</Platform>
    <SchemaVersion>2.0</SchemaVersion>
    <ProjectGuid>{guid}</ProjectGuid>
    <OutputType>Library</OutputType>
    <RootNamespace>{name}</RootNamespace>
    <AssemblyName>{name}</AssemblyName>
    <TargetFrameworkVersion>v4.5.2</TargetFrameworkVersion>
    <TargetFSharpCoreVersion>4.4.0.0</TargetFSharpCoreVersion>
    <TargetFrameworkProfile />
    <DocumentationFile>{name}.xml</DocumentationFile>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Debug|AnyCPU' ">
    <DebugSymbols>true</DebugSymbols>
    <DebugType>full</DebugType>
    <Optimize>false</Optimize>
    <Tailcalls>false</Tailcalls>
    <DefineConstants>DEBUG;TRACE</DefineConstants>
    <WarningLevel>3</WarningLevel>
  </PropertyGroup>
  <PropertyGroup Condition=" '$(Configuration)|$(Platform)' == 'Release|AnyCPU' ">
    <DebugType>pdbonly</DebugType>
    <Optimize>true</Optimize>
    <Tailcalls>true</Tailcalls>
    <DefineConstants>TRACE</DefineConstants>
    <WarningLevel>3</WarningLevel>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="mscorlib" />
    <Reference Include="System" />
    <Reference Include="System.Core" />
    <Reference Include="System.Numerics" />
    <Reference Include="FSharp.Core, Version=$(TargetFSharpCoreVersion), Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" />
{reference}
  </ItemGroup>
  <ItemGroup>
{compile}
  </ItemGroup>
  <PropertyGroup>
    <MinimumVisualStudioVersion Condition="'$(MinimumVisualStudioVersion)' == ''">11</MinimumVisualStudioVersion>
  </PropertyGroup>
  <Choose>
    <When Condition="'$(VisualStudioVersion)' == '11.0'">
      <PropertyGroup Condition="Exists('$(MSBuildExtensionsPath32)\..\Microsoft SDKs\F#\3.0\Framework\v4.0\Microsoft.FSharp.Targets')">
        <FSharpTargetsPath>$(MSBuildExtensionsPath32)\..\Microsoft SDKs\F#\3.0\Framework\v4.0\Microsoft.FSharp.Targets</FSharpTargetsPath>
      </PropertyGroup>
    </When>
    <Otherwise>
      <PropertyGroup Condition="Exists('$(MSBuildExtensionsPath32)\Microsoft\VisualStudio\v$(VisualStudioVersion)\FSharp\Microsoft.FSharp.Targets')">
        <FSharpTargetsPath>$(MSBuildExtensionsPath32)\Microsoft\VisualStudio\v$(VisualStudioVersion)\FSharp\Microsoft.FSharp.Targets</FSharpTargetsPath>
      </PropertyGroup>
    </Otherwise>
  </Choose>
  <Import Project="$(FSharpTargetsPath)" />
</Project>"""
)

COMPILE_TEMPLATE = r"""    <Compile Include="{}" />"""
REFERENCE_TEMPLATE = r"""    <Reference Include="{}" />"""

def parse(argv):
    """Parses command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("project", default="fableproject.json", help="JSON project file")
    return parser.parse_args(argv)


def uuid_of(text):
    return uuid.uuid5(uuid.NAMESPACE_DNS, text)

def escape_xml(text):
    return xml.sax.saxutils.escape(text)

def relative_path(path, source="."):
    return os.path.relpath(path, source)

def main(args):
    project_file = os.path.abspath(args.project)
    print("Loading: {}".format(project_file))
    with open(project_file, "r") as file:
        project = json.load(file)

    source_path = os.path.dirname(project_file)

    def fix_path(path):
        return os.path.abspath(os.path.join(source_path, path))
    def fix_paths(paths):
        return [fix_path(p) for p in paths]

    name = project.get("name", "project")
    guid = uuid_of(name)
    fsproj = fix_path(name + ".fsproj")

    reference = fix_paths(project.get("reference", []))
    compile = fix_paths(project.get("compile", []))

    target_path = os.path.dirname(fsproj)

    reference = [relative_path(p, target_path) for p in reference]
    compile = [relative_path(p, target_path) for p in compile]
    
    for r in reference:
        print("Reference: {}".format(r))
    for c in compile:
        print("Compile: {}".format(c))
    
    reference = [REFERENCE_TEMPLATE.format(escape_xml(p)) for p in reference]
    compile = [COMPILE_TEMPLATE.format(escape_xml(p)) for p in compile]

    project_template = PROJECT_TEMPLATE.format(
        name=escape_xml(name),
        guid=str(guid),
        reference='\n'.join(reference),
        compile='\n'.join(compile)
    )

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    with open(fsproj, "w") as file:
        print("Saving: {}".format(fsproj))
        file.write(project_template)

if __name__ == "__main__":
    argv = sys.argv[1:]
    sys.exit(main(parse(argv)))
