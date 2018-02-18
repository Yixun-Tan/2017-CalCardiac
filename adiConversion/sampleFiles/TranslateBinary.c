/***************************************************************************
 * Translate Binary for LabChart for Windows
 *
 * TranslateBinary.c
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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ADIBinaryFormat.h"

/*
 * Here is a simple example program.
 * It creates a file called test.bin which contains 2 channels of 16-bit data,
 * 800 samples in each channel, 100 samples per second.
 */
void main()
   {
   struct CFWBINARY cfwb;
   struct CFWBCHANNEL chan;
   short ch1,ch2;
   char title[CHANNEL_TITLE_LEN];
   FILE *output;
   short i;

   // Perform runtime check on cfwb and chan for correct size
   if (sizeof(struct CFWBINARY) != 68)
      {
      printf("The size of 'struct CFWBINARY' is not 68 bytes.\n");
      exit(1);
      }
   if (sizeof(struct CFWBCHANNEL) != 96)
      {
      printf("The size of 'struct CFWBCHANNEL' is not 96 bytes.\n");
      exit(1);
      }

   // Create the output file. It must end with the .bin suffix
   output = fopen("test.bin", "wb");
   if (output == NULL)
      {
      printf("Could not open test.bin\n");
      exit(1);
      }

   strncpy(cfwb.magic, "CFWB", 4);
   cfwb.Version = CFWB_VERSION;
   cfwb.secsPerTick = 0.01;   // 100 S/s
   cfwb.Year = 2001;
   cfwb.Month = 11;
   cfwb.Day = 29;
   cfwb.Hour = 14;
   cfwb.Minute = 0;
   cfwb.Second = 0;
   cfwb.trigger = -1.0;       // no pretrigger
   cfwb.NChannels = 2;
   cfwb.SamplesPerChannel = 800;
   // no time channel interleaved within the data
   // (as of v1.3 of Translate Binary the time channel is ignored anyway)
   cfwb.TimeChannel = 0;
   cfwb.DataFormat = 3;       // 16-bit data

   // Write out the file header
   fwrite(&cfwb, sizeof(cfwb), 1, output);

   // Write out 'NChannels' of channel headers
   for (i = 0; i < cfwb.NChannels; i++)
      {
      // Set channel titles and units
      sprintf(title, "Signal %d", i + 1);
      strncpy(chan.Title, title, CHANNEL_TITLE_LEN);
      strncpy(chan.Units, "Volts", UNITS_LEN);

      chan.RangeHigh = 0;  // These are not currently used
      chan.RangeLow = 0;   // (up to and including v1.3 of Translate Binary)

      // scale and offset are used to convert 16-bit samples into user units where
      // data = scale * (sample + offset)
      // For floating point data, set scale = 1.0 and offset = 0.0
      chan.scale = 1.0 / 16000.0;
      chan.offset = 0.0;
      fwrite(&chan, sizeof(chan), 1, output);
      }

   // Write out the interleaved channel data
   for (i = 0; i < cfwb.SamplesPerChannel; i++)
      {
      // create some example data
      ch1 = 20 * i;  // an ascending ramp 0 -> +1 Volts
      ch2 = -20 * i; // a descending ramp 0 -> -1 Volts
      fwrite(&ch1, sizeof(short), 1, output);
      fwrite(&ch2, sizeof(short), 1, output);
      }

   // all done, close file
   fclose(output);
   }
t), 1, output);
      fwrite(&ch2, sizeof(short), 1, output);
      }

   // all done, close file
   fclose(output);
   }