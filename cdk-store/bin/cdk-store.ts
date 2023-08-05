#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CdkStoreStack } from '../lib/cdk-store-stack';

const app = new cdk.App();
new CdkStoreStack(app, 'CdkStoreStack');
