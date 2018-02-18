/***************************************************************************
 * Translate Binary for LabChart for Windows
 *
 * ADIBinaryFormat.h
 *
 * Copyright (c) 2001-2009 ADInstruments Ltd.
 *
 * Translate Binary is a LabChart for Windows extension that enables data to be
 * moved to and from LabChart, in a simple binary format.
 *
 * A LCfW binary file has the following structure:
 *
 *  - A 68 byte file header (CFWBINARY structure) containing basic information
 *   about the data such as the sampling period, number of channels, trigger
 *   time, data format.
 *
 *  - For each channel, a 96 byte channel header (CFWBCHANNEL structure)
 *   containing information about the channel.
 *
 *  - The interleaved channel data. Data can be either double precision
 *   floating point, single precision floating point or 16 bit integer, as
 *   specified by the DataFormat parameter of the file header.
 *
 *
 * The CFWBINARY and CFWBCHANNEL structures are defined below, along with a
 * simple program which creates a two channel CfW binary file.
 *
 * Note that the following types must have the indicated size and that the
 * program needs to be run on a little endian machine (e.g. x86):
 *
 * sizeof(char)   = 1 byte
 * sizeof(short)  = 2 bytes
 * sizeof(long)   = 4 bytes
 * sizeof(double) = 8 bytes, i.e. 64 bit IEEE floating point
 *
 ******************************************************************************/
#ifndef _ADIBinFormat
#define _ADIBinFormat

#define CHANNEL_TITLE_LEN  32
#define UNITS_LEN          32
#define CFWB_VERSION       1

enum 
   {
   kBinFmtDouble  =  1,
   kBinFmtFloat,
   kBinFmtInt16,
   };

// The file and header structures must be packed on 1-byte boundaries.
// On Visual C++ the following pragma enforces this.
#pragma pack(1)

// Each LabChart for Windows binary file starts with the following structure:
struct CFWBINARY
   {
   char     magic[4];            // always "CFWB"
   long     Version;             // = CFWB_VERSION
   double   secsPerTick;         // sampling interval in seconds

   // Trigger Date and time information
   long    Year;                // 4 digit year
   long    Month;               // months 1 - 12
   long    Day;                 // days 1 - 31
   long    Hour;                // hours 0 - 23
   long    Minute;              // minutes 0 - 59
   double   Second;              // seconds
   double   trigger;             // Amount of pretrigger data in seconds.

   long     NChannels;           // Number of channels
   long     SamplesPerChannel;   // Number of sample points per channel
   
   // The TimeChannel flag indicates that the sample time of each sample is
   // interleaved as the first column of data. This is only valid for the floating
   // point data formats. For all releases of TranslateBinary up to and including
   // v1.3, sample time data can be included but it is not used.
   long     TimeChannel;         // 1 = time included as first channel, 0 = not included
   long     DataFormat;          // 1 = double , 2 = float, 3 = 16-bit integer
   };

// Then one of these for each of the 'NChannels':
struct CFWBCHANNEL
   {
   char     Title[CHANNEL_TITLE_LEN];  // Channel title string
   char     Units[UNITS_LEN];          // Channel units string

   // scale and offset are used to convert 16-bit samples into user units,
   // where  data = scale * (sample + offset)
   double   scale;                     // scale (= 1.0 for floating point data)
   double   offset;                    // offset (= 0.0 for floating point data)

   // The maximum and minimum values of the data
   // (not used in TranslateBinary up to and including v1.3)
   double   RangeHigh;
   double   RangeLow;
   };

// Back to default data structure packing
// #pragma pack()

// #endif   // sentinelRangeLow;

// Back to default data structure packing
// #pragma pack()

// #endif   // sentinel