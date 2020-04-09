#
# Copyright (C) 2019 GreenWaves Technologies
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import runner.rtl.rtl_runner
import os

class Runner(runner.rtl.rtl_runner.Runner):

    def __init__(self, args, config):
        super(Runner, self).__init__(args, config)
        self.__process_args()

        self.set_arg('-gSPI_FLASH_LOAD_MEM=3')
        #self.set_arg('-gCONFIG_FILE=rtl_config.json')
        #self.set_arg('-sv_lib %s' % (os.path.join(os.environ.get('INSTALL_DIR'), 'lib', 'libpulpdpi')))

        if os.environ.get('QUESTA_CXX') is not None:
            self.set_arg('-dpicpppath ' + os.environ.get('QUESTA_CXX'))

        self.set_arg('-permit_unmatched_virtual_intf')
        self.set_arg('+preload_file=efuse_preload.data')
        self.set_arg('-gBAUDRATE=115200')

        self.set_env('VOPT_ACC_ENA', 'YES')


    def flash(self):
        path = os.path.join(self.config.get_str('gapy/work_dir'), 'efuse_preload.data')
        self.gen_efuse_stim(path)
        return runner.rtl.rtl_runner.Runner.flash(self)



    def gen_efuse_stim(self, filename):
        self.dump('Creating efuse stimuli')

        nb_regs = 128
        efuses = [0] * nb_regs

          # RTL platform | flash boot | no encryption | no wait xtal
        efuses[0] = 2 | (2 << 3) | (0 << 4) | (0 << 5) | (0 << 6) | (0 << 7)
        efuses[39] = 0x2   # Boot on UDMA SPIM1 interface (first single spi)


        self.dump('  Generating to file: ' + filename)

        with open(filename, 'w') as file:
            for efuseId in range (0, 128):
                value = efuses[efuseId]
                self.dump('  Writing register (index: %d, value: 0x%x)' % (efuseId, value))
                file.write('{0:032b}\n'.format(value))
  

    def dump(self, str):
        if self.verbose:
            print (str)
