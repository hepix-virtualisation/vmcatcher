


class EventObj(object):
    def __init__(self,eventExecutionString):
        self.eventExecutionString = eventExecutionString
        self.env = os.environ
        self.log = logging.getLogger("Events")
    def launch(self,env):
        process = subprocess.Popen([self.eventExecutionString], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,env=env)
        processRc = None
        handleprocess = True
        counter = 0
        stdout = ''
        stderr = ''
        timeout = 10
        while handleprocess:
            counter += 1
            cout,cerr = process.communicate()
            stdout += cout
            stderr += cerr
            process.poll()
            processRc = process.returncode
            if processRc != None:
                break
            if counter == timeout:
                os.kill(process.pid, signal.SIGQUIT)
            if counter > timeout:
                os.kill(process.pid, signal.SIGKILL)
                processRc = -9
                break
            time.sleep(1)
        return (processRc,stdout,stderr)

    def eventProcess(self,EventStr,metadata):
        # Note keys 'sha512', 'uuid','size' are depricated.
        mappingdict = {'sha512' : 'VMCATCHER_EVENT_SL_CHECKSUM_SHA512',
            'uuid' : 'VMCATCHER_EVENT_DC_IDENTIFIER',
            'size' : 'VMCATCHER_EVENT_HV_SIZE',
            'sha512' : 'VMCATCHER_EVENT_SL_CHECKSUM_SHA512',
            # End of depricated options
            'filename' : 'VMCATCHER_EVENT_FILENAME',
            'dc:identifier' : 'VMCATCHER_EVENT_DC_IDENTIFIER',
            'hv:uri' : 'VMCATCHER_EVENT_HV_URI',
            'hv:size' : 'VMCATCHER_EVENT_HV_SIZE',
            'dc:description' : 'VMCATCHER_EVENT_DC_DESCRIPTION',
            'dc:title' : 'VMCATCHER_EVENT_DC_TITLE',
            'hv:hypervisor' : 'VMCATCHER_EVENT_HV_HYPERVISOR',
            'hv:version' : 'VMCATCHER_EVENT_HV_VERSION',
            'sl:arch' : 'VMCATCHER_EVENT_SL_ARCH',
            'sl:comments' : 'VMCATCHER_EVENT_SL_COMMENTS',
            'sl:os' : 'VMCATCHER_EVENT_SL_OS',
            'sl:osversion' : 'VMCATCHER_EVENT_SL_OSVERSION',
            'sl:checksum:sha512' : 'VMCATCHER_EVENT_SL_CHECKSUM_SHA512'}
        newEnv = self.env
        newEnv['VMCATCHER_EVENT_TYPE'] = EventStr
        for key in mappingdict.keys():
            if key in metadata.keys():
                newEnv[str(mappingdict[key])] = str(metadata[key])
        rc,stdout,stderr = self.launch(newEnv)
        if rc == 0:
            self.log.debug("event '%s' executed '%s'" % (newEnv['VMCATCHER_EVENT_TYPE'],self.eventExecutionString))
            self.log.debug("stdout=%s" % (stdout))
            self.log.debug("stderr=%s" % (stderr))
        else:
            self.log.error("Event '%s' executed '%s' with exit code '%s'." % (newEnv['VMCATCHER_EVENT_TYPE'],self.eventExecutionString,rc))
            self.log.info("stdout=%s" % (stdout))
            self.log.info("stderr=%s" % (stderr))
        return
    def eventImageNew(self,metadata):
        self.eventProcess("ImageNew",metadata)


