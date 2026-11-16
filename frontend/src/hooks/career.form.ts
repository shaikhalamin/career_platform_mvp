import { createFormHook } from '@tanstack/react-form'

import {
  ChipsField,
  LanguageRowsField,
  SelectField,
  SliderField,
  SubscribeButton,
  TextArea,
  TextField,
  TriStateSwitchField,
  WorkAuthRowsField,
} from '../components/career-form-fields'
import { fieldContext, formContext } from './form-contexts'

export const { useAppForm } = createFormHook({
  fieldComponents: {
    TextField,
    SelectField,
    SliderField,
    ChipsField,
    LanguageRowsField,
    WorkAuthRowsField,
    TriStateSwitchField,
    TextArea,
  },
  formComponents: {
    SubscribeButton,
  },
  fieldContext,
  formContext,
})
